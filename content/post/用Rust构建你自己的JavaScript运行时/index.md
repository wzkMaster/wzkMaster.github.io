---
title: "[译] 用 Rust 构建你自己的 JavaScript 运行时（1）"
date: 2023-08-02
comments: true
description: 在这篇文章中我们将创建一个自定义的 JavaScript 运行时，它能够执行本地 JavaScript 文件，与文件系统交互，并且有一个简化版的 console API。
image: deno.png
---

> 原文链接: https://deno.com/blog/roll-your-own-javascript-runtime
>
> 原文作者：[Bartek Iwańczuk](https://github.com/bartlomieju)
>
> 为了大家能够读的更爽，本文**全部由本人手工翻译而成**，没有任何机翻内容，如果大家有收获的话，还请多多点赞收藏支持～

在这篇文章中我们将创建一个自定义的 JavaScript 运行时，我们就叫它 `runjs` 吧！可以把它认为是一个简化版的 `deno`（一个类似于 `node` 的 JS 运行时）我们的目标是创建一个 CLI（命令行程序），它能够执行本地 JavaScript 文件，读取文件、写入文件、删除文件，并且有一个简化版的 `console` API。

## 前置要求

这篇教程需要读者掌握以下内容：

- 基本的 Rust 知识
- 对 JavaScript 事件循环的基本了解

确保你的电脑上已经安装了 Rust（以及 `cargo`，Rust 的包管理器），其版本不能低于 `1.62.0`。访问 [rust-lang.org](https://www.rust-lang.org/learn/get-started) 来安装 Rust 编译器和 `cargo`。

运行下面这行命令来确保我们能够继续前进：

```bash
$ cargo --version
cargo 1.62.0 (a748cf5a3 2022-06-08)
```

## Hello, Rust!

首先，我们来创建一个新的 Rust 项目，初始化一个名叫 `runjs` 的二进制包。

```bash
$ cargo init --bin runjs
     Created binary (application) package
```

进入 `runjs` 文件夹并在你的编辑器中打开它。运行 `cargo run` 来确认我们正确地初始化了项目。

```bash
$ cd runjs
$ cargo run
   Compiling runjs v0.1.0 (/Users/ib/dev/runjs)
    Finished dev [unoptimized + debuginfo] target(s) in 1.76s
     Running `target/debug/runjs`
Hello, world!
```

如果一切顺利的话，我们就可以开始创建我们自己的 JavaScript 运行时了！

## 依赖安装

接下来，我们添加 `deno_core` 和 `tokio` 依赖包到项目中。

```bash
$ cargo add deno_core
    Updating crates.io index
      Adding deno_core v0.142.0 to dependencies.
$ cargo add tokio --features=full
    Updating crates.io index
      Adding tokio v1.19.2 to dependencies.
```

更新后的 `Cargo.toml` 文件应该长这样子：

```toml
[package]
name = "runjs"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
deno_core = "0.142.0"
tokio = { version = "1.19.2", features = ["full"] }
```

`deno_core` 由 Deno 团队创建，用于抽象简化与 V8 JavaScript 引擎之间的交互。V8 是一个包含了数千个 API 的复杂项目，为了让大家能够更方便地使用它，`deno_core` 提供了一个 `JsRuntime` 结构体，其中封装了一个 V8 引擎实例（它叫 `Isolate`）并提供了整合事件循环的能力。

`tokio` 是一个异步的 Rust 运行时，我们将用它来作为事件循环。 Tokio 将负责与操作系统的交互，如文件读写、网络访问等。`tokio` 和 `deno_core` 让我们能够轻松地将 JavaScript 的 `Promise` 映射为 Rust 的 `Future` 。

有了 JavaScript 引擎和事件循环，我们正式开始 JS 运行时的构建。

## Hello, runjs!

我们首先编写一个异步的 Rust 函数来创建一个 `JsRuntime` 实例，它将负责 JS 代码的执行。

```rust
// main.rs
use std::rc::Rc;
use deno_core::error::AnyError;

async fn run_js(file_path: &str) -> Result<(), AnyError> {
  let main_module = deno_core::resolve_path(file_path)?;
  let mut js_runtime = deno_core::JsRuntime::new(deno_core::RuntimeOptions {
      module_loader: Some(Rc::new(deno_core::FsModuleLoader)),
      ..Default::default()
  });

  let mod_id = js_runtime.load_main_module(&main_module, None).await?;
  let result = js_runtime.mod_evaluate(mod_id);
  js_runtime.run_event_loop(false).await?;
  result.await?
}

fn main() {
  println!("Hello, world!");
}
```

这段代码信息量很大。`run_js` 异步函数创建了一个 `JsRuntime` 实例，它使用了基于文件系统的模块加载器。随后，我们往 `js_runtime` 运行时中导入了一个模块，运行它，最后启动一个事件循环。

`run_js` 函数封装了整个 JavaScript 代码的运行生命周期。在我们开始正式运行代码之前，得先创建一个单线程的 `tokio` 运行时来运行我们的 `run_js` 函数。

```rust
// main.rs
fn main() {
  let runtime = tokio::runtime::Builder::new_current_thread()
    .enable_all()
    .build()
    .unwrap();
  if let Err(error) = runtime.block_on(run_js("./example.js")) {
    eprintln!("error: {}", error);
  }
}
```

现在我们可以来尝试着运行一些 JavaScript 代码了！创建一个 `example.js` 文件，其功能是打印 `Hello runjs!`。

```js
// example.js
Deno.core.print("Hello runjs!");
```

> 这里我们使用了 `Deno.core` 的 `print` 函数 - 它是由 `deno_core` 提供的一个内置全局变量。

现在运行它：

```bash
$ cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 0.05s
     Running `target/debug/runjs`
	Hello runjs!⏎
```

成功了！仅仅用了 25 行 Rust 代码，我们就创建了一个简单的 JavaScript 运行时，它可以执行我们的本地 JS 文件。当然现在这个运行时并没有太多的功能（例如，现在 `console.log` 是没有效果的，不信你试试！），但我们已经把一个 V8 引擎和 `tokio` 集成到我们的项目中了。

## 添加 `console` API

现在我们来添加 `console` API。首先，创建 `src/runtime.js` 文件，这个文件用于实例化 `console` 对象，使其全局可用。

```js
// runtime.js
((globalThis) => {
  const core = Deno.core;

  function argsToMessage(...args) {
    return args.map((arg) => JSON.stringify(arg)).join(" ");
  }

  globalThis.console = {
    log: (...args) => {
      core.print(`[out]: ${argsToMessage(...args)}\n`, false);
    },
    error: (...args) => {
      core.print(`[err]: ${argsToMessage(...args)}\n`, true);
    },
  };
})(globalThis);
```

`console.log` 和 `console.error` 函数接收多个参数，将这些参数交给 `JSON.stringlify` 处理（这样我们才能打印对象类型），然后在打印内容之前添加 `out` 或 `error` 前缀。这是一种老式的 JS 写法，就像我们在 ES module 出现之前在浏览器中写的那样。

为了确保我们不会污染全局作用域，我们把代码放在一个立即执行函数（IIFE）中运行。如果我们没有这么做，`argsToMessage` 函数就会被暴露在我们的运行时的全局作用域中。

现在我们把这份代码添加到我们的二进制文件中，在每次运行时执行它：

```rust
let mut js_runtime = deno_core::JsRuntime::new(deno_core::RuntimeOptions {
  module_loader: Some(Rc::new(deno_core::FsModuleLoader)),
  ..Default::default()
});
// 添加这行
js_runtime.execute_script("[runjs:runtime.js]",  include_str!("./runtime.js")
```

现在，我们在 `example.js` 中使用我们的 `console` API：

```js
console.log("Hello", "runjs!");
console.error("Boom!");
```

再次运行它：

```bash
$ cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 0.05s
     Running `target/debug/runjs`
[out]: "Hello" "runjs!"
[err]: "Boom!"
```

成功了！现在我们来添加文件系统相关的 API。

## 添加基础文件系统 API

首先我们更新一下 `runtime.js` 文件：

```js
((globalThis) => {
  // ...

  core.initializeAsyncOps();
  globalThis.runjs = {
    readFile: (path) => {
      return core.ops.op_read_file(path);
    },
    writeFile: (path, contents) => {
      return core.ops.op_write_file(path, contents);
    },
    removeFile: (path) => {
      return core.ops.op_remove_file(path);
    },
  };
})(globalThis);
```

我们添加了一个新的全局对象 `runjs` ，它有三个方法：`readFile`，`writeFile`，`removeFile`。前两个方法是异步的，最后一个方法是同步的。

你可能会疑惑那些 `core.ops.[操作名称]` 的代码是什么 - 它们是 `deno_core` 包提供的绑定 JavaScript 和 Rust 函数的能力。当你调用上面的方法时，`deno_core` 会寻找拥有 `#[op]` 属性和对应名称的函数进行调用。

我们更新 `main.rs` 文件来看看效果：

```rust
// ...
use deno_core::op;
use deno_core::Extension;
#[op]
async fn op_read_file(path: String) -> Result<String, AnyError> {
    let contents = tokio::fs::read_to_string(path).await?;
    Ok(contents)
}

#[op]
async fn op_write_file(path: String, contents: String) -> Result<(), AnyError> {
    tokio::fs::write(path, contents).await?;
    Ok(())
}

#[op]
fn op_remove_file(path: String) -> Result<(), AnyError> {
    std::fs::remove_file(path)?;
    Ok(())
}
// ...
```

我们添加了三个可以在 JavaScript 中调用的操作。但要想让这些操作能够被 JavaScript 调用，我们还需要通过注册一个 `Extension` 来让 `deno_core` 知道这些操作函数。

```rust
async fn run_js(file_path: &str) -> Result<(), AnyError> {
  let main_module = deno_core::resolve_path(file_path)?;
  let runjs_extension = Extension::builder()
      .ops(vec![
          op_read_file::decl(),
          op_write_file::decl(),
          op_remove_file::decl(),
      ])
      .build();
  let mut js_runtime = deno_core::JsRuntime::new(deno_core::RuntimeOptions {
      module_loader: Some(Rc::new(deno_core::FsModuleLoader)),
      extensions: vec![runjs_extension],
      ..Default::default()
  });

  // ...
}
```

Extension 让你能够配置你的 `JsRuntime` 实例，将不同的 Rust 函数暴露给 JavaScript，同时还能让你进行更高级的操作，例如加载额外的 JavaScript 代码。

让我们再更新一下 `example.js`：

```js
console.log("Hello", "runjs!");
console.error("Boom!");

const path = "./log.txt";
try {
  const contents = await runjs.readFile(path);
  console.log("Read from a file", contents);
} catch (err) {
  console.error("Unable to read file", path, err);
}

await runjs.writeFile(path, "I can write to a file.");
const contents = await runjs.readFile(path);
console.log("Read from a file", path, "contents:", contents);
console.log("Removing file", path);
runjs.removeFile(path);
console.log("File removed");
```

运行它：

```
$ cargo run
   Compiling runjs v0.1.0 (/Users/ib/dev/runjs)
    Finished dev [unoptimized + debuginfo] target(s) in 0.97s
     Running `target/debug/runjs`
[out]: "Hello" "runjs!"
[err]: "Boom!"
[err]: "Unable to read file" "./log.txt" {"code":"ENOENT"}
[out]: "Read from a file" "./log.txt" "contents:" "I can write to a file."
[out]: "Removing file" "./log.txt"
[out]: "File removed"
```

太棒了，我们的 `runjs` 运行时现在可以和文件系统进行交互了！我们只用了寥寥数行代码就让 JavaScript 拥有了调用 Rust 函数的能力 - `deno_core` 帮我们处理了两种编程语言之间数据转换和通信的问题，我们不需要自己手动处理这些麻烦。

## 总结

在这篇文章中，我们创建了一个 Rust 项目，将一个强大的 JavaScript 引擎（`V8`）和一个高性能的事件循环库（`tokio`）集成在一起，从而构建了一个简单的自定义 JavaScript 运行时。
