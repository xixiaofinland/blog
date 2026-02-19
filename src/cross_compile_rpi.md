# Cross-Compiling ZeroClaw for Raspberry Pi on NixOS
*2026-02-19*

I have [zeroclaw](https://github.com/zeroclaw-labs/zeroclaw) that I wanted to run on a Raspberry Pi
5 (Ubuntu 24.04 LTS, aarch64). My development machine is a NixOS x86_64 desktop.
The goal: compile on the desktop, deploy to the Pi—without touching the Pi's
package manager or installing a Rust toolchain there.

This post documents how I got it working using a Nix **devShell**, and the
several issues that came up along the way.

---

## The Plan: devShell, not a Nix derivation

The first design decision was *how* to drive the cross-compilation inside Nix.
Two options exist:

- **Nix derivation/package** — let Nix build and manage the output as a store
  path.
- **devShell** — enter a shell that has the cross-toolchain on `PATH` and run
  `cargo build` manually.

I chose the devShell approach. zeroclaw is not a Nix-managed package, it lives
at `~/zeroclaw/` as a normal checkout. I just needed the right compiler
environment available when I ran `cargo build`.

---

## Setting Up the devShell

I added a `zeroclaw-cross` entry to the `devShells` output in `flake.nix`. The
key ingredients:

- `pkgsCross` instantiated for `aarch64-multiplatform` via
  `lib.systems.examples.aarch64-multiplatform`
- `rust-overlay` overlays threaded through so `rust-bin.stable."1.92.0"` (the
  version pinned in zeroclaw's `rust-toolchain.toml`) is available
- The aarch64 GCC cross-toolchain from `pkgsCross.stdenv.cc`
- `openssl` and `postgresql` from `pkgsCross.pkgsStatic` for static linking

The relevant env vars exposed in the shell:

```nix
CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER =
  "${pkgsCross.stdenv.cc}/bin/aarch64-unknown-linux-gnu-gcc";
CC_aarch64_unknown_linux_gnu =
  "${pkgsCross.stdenv.cc}/bin/aarch64-unknown-linux-gnu-gcc";
CXX_aarch64_unknown_linux_gnu =
  "${pkgsCross.stdenv.cc}/bin/aarch64-unknown-linux-gnu-g++";
AR_aarch64_unknown_linux_gnu =
  "${pkgsCross.stdenv.cc}/bin/aarch64-unknown-linux-gnu-ar";
```

Because `forAllSystems` in my flake only covers `x86_64-linux` and
`x86_64-darwin`, the shell was added outside that helper using a `//` merge on
the `devShells` output:

```nix
devShells = forAllSystems (...) // {
  "x86_64-linux" = devShells."x86_64-linux" // {
    zeroclaw-cross = pkgs.mkShell { ... };
  };
};
```

the full flake.nix is [here](https://github.com/xixiaofinland/dotfiles-nix/blob/f643acbd8df60065689e2380f5684f15e015e82b/flake.nix#L391).

Then entering the shell and building is just:

```bash
nix develop .#zeroclaw-cross
cd ~/zeroclaw
cargo build --release --target aarch64-unknown-linux-gnu
```

---

## Issue 1: C crates ignoring the cross-compiler

The first build attempt failed midway with ARM assembly errors inside `blake3`
and `aws-lc-sys`. The error looked roughly like:

```
error: unknown directive
  .arch armv8-a
```

This is the classic sign that the **C compiler used by the `cc` crate is the
host `gcc`**, not the cross `gcc`. Setting only
`CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER` is not enough. That variable
tells Cargo which linker to use for the final link step, but crates that compile
C/C++/asm via the `cc` crate look at a different set of env vars:

```
CC_aarch64_unknown_linux_gnu
CXX_aarch64_unknown_linux_gnu
AR_aarch64_unknown_linux_gnu
```

Adding all four variables to the devShell fixed the issue. The build then
completed in about 3.5 minutes.

---

## Issue 2: Binary hardcoded to the Nix store interpreter

With the binary built, I copied it to the Pi:

```bash
scp ~/zeroclaw/target/aarch64-unknown-linux-gnu/release/zeroclaw \
    ubuntu@192.168.1.109:~/.cargo/bin/zeroclaw
```

Running it on the Pi gave:

```
bash: /home/ubuntu/.cargo/bin/zeroclaw: cannot execute: required file not found
```

Checking the ELF interpreter with `readelf` revealed the problem:

```
[Requesting program interpreter: /nix/store/ghvpbda663vmf62g22d9y47z55yh43xn-glibc-aarch64-unknown-linux-gnu-2.42-47/lib/ld-linux-aarch64.so.1]
```

The binary was built against the **Nix glibc**, so its dynamic linker path
points into `/nix/store/`—a path that simply doesn't exist on Ubuntu. The fix is
`patchelf`, which rewrites the ELF header in-place:

```bash
nix shell nixpkgs#patchelf -- patchelf \
  --set-interpreter /lib/ld-linux-aarch64.so.1 \
  --set-rpath "" \
  ~/zeroclaw/target/aarch64-unknown-linux-gnu/release/zeroclaw
```

After patching, `readelf -l` showed the standard Ubuntu interpreter path, and
the binary ran on the Pi straight away:

```
$ zeroclaw --version
zeroclaw 0.1.0
```

---

## Summary

The full flow that worked:

1. Add a `zeroclaw-cross` devShell to `flake.nix` with `pkgsCross` for
   `aarch64-multiplatform` and all four cross-compiler env vars set.
2. Enter the shell and run `cargo build --release --target
   aarch64-unknown-linux-gnu` inside the project directory.
3. Patch the ELF interpreter with `patchelf --set-interpreter
   /lib/ld-linux-aarch64.so.1`.
4. `scp` the patched binary to the Pi.

Two non-obvious gotchas to keep in mind:

- The `cc` crate uses `CC_<target>` / `CXX_<target>` / `AR_<target>`, not the
  Cargo linker variable—you need all of them for crates with C/asm code.
- Nix-built binaries embed the Nix store path as the ELF interpreter. Always
  `patchelf` before deploying to a non-Nix system.
