# Common Traits

Let's briefly explore some standard library traits to understand their practical
use.

- Debug
- Display
- Default
- Clone
- Copy
- From/Into
- Eq and PartialEq
- Ord and PartialOrd

These traits enable a rich set of tools that work seamlessly across many types.
Let’s look at a few examples to illustrate their usefulness.

## Debug

When we build a custom struct, like the `Point` below, we'd often like to
display the content to the users. If we `println!` as below, it doesn't work.
Click the "run" button in the code below and see what the compiler tells.

```rust,does_not_compile
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let origin = Point { x: 0, y: 0 };
    println!("{}", origin); // not work
}
```

The compiler error implies that the `Point` needs to implement `std::fmt::Display` in
order for the line `println!("{}", origin)` to execute. We will discuss
`Display` trait in a minute. Now, we'd like to check the more common trait
`Debug`.

The `Debug` trait enables us to inspect the content by by allowing types to be
printed using the `{:?}` formatter in macros like `println!`.

```rust
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let origin = Point { x: 0, y: 0 };
    println!("{:?}", origin); // Output: Point { x: 0, y: 0 }
```

As shown in the 1st line, the easist way to implement Debug trait is to derive
it explicitly with `#[derive(Debug)]`, and then `{:?}` works now!

## Display

Now it's `Display`. Unlike Debug, the Display trait is for user-facing output.
Implementing it requires us to define how the type should look when printed.

```rust
use std::fmt;

struct Point {
    x: i32,
    y: i32,
}

impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

fn main() {
    let p = Point { x: 3, y: 4 };
    println!("{}", p); // Output: (3, 4)
}

```

You might have noticed that there is no `#[derive(Display)]` here. This is
because Rust’s standard library doesn’t provide such a macro, but there are
external crate like [derive_more](https://crates.io/crates/derive_more) to get
this functionality.

Speaking of `Debug` v.s. `Display`, if the type is meant to be readable by
users, implement `Display`. If it’s for developers, implement `Debug`. We can do
both.

## Default

The Default trait defines what it means to create a "default" value of a type.
It is often used when initializing structures with default configurations.

```rust
#[derive(Debug,Default)]
struct Config {
    debug_mode: bool,
    max_connections: u32,
}

fn main() {
    let config = Config::default(); // All fields set to their default values
    println!("{:?}", config); // Let's print the content out
}
```

If you run the code above, the result is `Config { debug_mode: false, max_connections: 0 }`.

Let's take a close look at the above code.

We have derived `Debug` in
order to prinln with `{:?}`. And we have also derived `Default`. Rust
allows us to derive `Default` because both of the two fields (`bool` and `u32`)
have implemented `Default` trait, with values *false* and *0* respectively.

Be aware that many Rust types do not implement Default. It is
only implemented when it makes sense to define a "reasonable default value". For
example, `std::fs::File`. Opening or creating a file requires a path — no
default makes sense.

```rust,does_not_compile
use std::fs::File;

#[derive(Debug, Default)]
struct Config {
    debug_mode: bool,
    max_connections: u32,
    file: File, // compiler complains here
}

fn main() {
    let config = Config::default();
    println!("{:?}", config);
}
```

## Clone and Copy
## From/Into
## Eq and PartialEq
## Ord and PartialOrd
