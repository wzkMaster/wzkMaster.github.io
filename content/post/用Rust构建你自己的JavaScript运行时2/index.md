---
title: "[译] 用 Rust 构建你自己的 JavaScript 运行时（2）"
date: 2023-08-04
comments: true
description: 在这篇文章中，我们在前一篇文章的基础上做这三件事：实现 `fetch`；读取一个文件路径作为命令行参数；支持 TypeScript 和 TSX
image: deno.png
---

> 原文链接: https://deno.com/blog/roll-your-own-javascript-runtime-pt2
>
> 原文作者：[Bartek Iwańczuk](https://github.com/bartlomieju)
>
> 为了大家能够读的更爽，本文**全部由本人手工翻译而成**，没有任何机翻内容，如果大家有收获的话，还请多多点赞收藏支持～

这是用 Rust 构建自定义 JavaScript 运行时的第二篇，第一篇[在这里]()。

有很多理由能够促使你构建一个自定义的 JavaScript 运行时，例如搭建一个用 Rust 作为后端的可交互 Web 应用，通过插件系统扩展你的平台，或者给“我的世界”游戏编写一个插件。

在这篇文章中，我们在前一篇文章的基础上做这三件事：

- 实现 `fetch`
- 读取一个文件路径作为命令行参数
- 支持 TypeScript 和 TSX

_你也可以 [查看视频教程](https://www.youtube.com/watch?v=-8L3_OOeENo) 或 [阅读源代码](https://github.com/denoland/roll-your-own-javascript-runtime)_

## 准备工作

如果你有跟着[第一篇]()文章一路敲下来，你的项目中应该包含了三个文件：

- `example.js`：用于执行并测试我们的运行时的 JS 文件。
- `main.rs`：创建了一个 `JsRuntime` 实例的异步函数，负责 JS 代码的执行。

- `runtime.js`：定义并提供了与 `main.rs` 中的 `JsRuntime` 进行交互的运行时接口。

接下来，让我们在运行时中实现一个 HTTP 函数 `fetch`。

## 实现 `fetch`

在我们的 `runtime.js` 文件中，添加一个新函数 `fetch` 在全局对象 `runjs` 中。

```js
// runtime.js

((globalThis) => {
  // ...

  globalThis.runjs = {
    readFile: (path) => {
      return ops.op_read_file(path);
    },
    writeFile: (path, contents) => {
      return ops.op_write_file(path, contents);
    },
    removeFile: (path) => {
      return ops.op_remove_file(path);
    },
    // 添加 fetch
    fetch: (url) => {
      return ops.op_fetch(url);
    },
  };
})(globalThis);
```

现在，我们需要在 `main.rs` 中定义 `op_fetch`。它是一个异步函数，接受一个 `String` 参数，返回一个 `String` 或者一个错误。

在这个函数中，我们将使用[`reqwest` 包](https://docs.rs/reqwest/latest/reqwest/)，它是一个方便而强大的 HTTP 库，我们只会用到它的 `get` 函数。

```rust
// main.rs

// …

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

// 添加 op_fetch 函数
#[op]
async fn op_fetch(url: String) -> Result<String, AnyError> {
  let body = reqwest::get(url).await?.text().await?;
  Ok(body)
}

// …
```

为了能够使用 `reqwest`，我们需要通过命令行把它添加到项目中：

```
$ cargo add reqwest
```

接下来，我们在 `run_js` 中注册 `op_fetch` 函数：

```rust
// main.rs

// …

async fn run_js(file_path: &str) -> Result<(), AnyError> {
  let main_module = deno_core::resolve_path(file_path)?;
  let runjs_extension = Extension::builder("runjs")
    .ops(vec![
      op_read_file::decl(),
      op_write_file::decl(),
      op_remove_file::decl(),
      op_fetch::decl(),  // 添加这一行
    ])
    .build();
// …

```

我们更新 `example.js` 来试验我们新添加的 `fetch` 函数：

```js
console.log("Hello", "runjs!");
content = await runjs.fetch(
  "https://deno.land/std@0.177.0/examples/welcome.ts"
);
console.log("Content from fetch", content);
```

通过下面的命令运行它：

```
$ cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 2m 14s
     Running `target/debug/runjs`
[out]: "Hello" "runjs!"
[out]: "Content from fetch" "// Copyright 2018-2023 the Deno authors. All rights reserved. MIT license.\n\n/** Welcome to Deno!\n *\n * @module\n */\n\nconsole.log(\"Welcome to Deno!\");\n"
```

成功了！我们用了不到 10 行代码就把自定义的 `fetch` 函数添加到了 JavaScript 运行时中。

## 读取命令行参数

到目前为止，我们都是把加载和运行的文件路径写死的。我们只需要运行 `cargo run` 就可以执行 `example.js` 中的内容。

让我们来更新 `runjs` ，使其能够读取命令行的参数，将第一个参数作为要运行的代码的文件路径。我们可以在 `main.rs` 的 `main()` 函数中进行更改：

```rust
// main.rs

// ...

fn main() {
  let args: Vec<String> = std::env::args().collect();

  if args.is_empty() {
      eprintln!("Usage: runjs <file>");
      std::process::exit(1);
  }

  let file_path = &args[1];

  let runtime = tokio::runtime::Builder::new_current_thread()
    .enable_all()
    .build()
    .unwrap();
   if let Err(error) = runtime.block_on(run_js(file_path)) {
     eprintln!("error: {error}");
   }
}
```

我们运行 `cargo run example.js` 试试看：

```
$ cargo run example.js
    Finished dev [unoptimized + debuginfo] target(s) in 6.99s
     Running `target/debug/runjs example.js`
[out]: "Hello" "runjs!"
[out]: "Content from fetch" "// Copyright 2018-2023 the Deno authors. All rights reserved. MIT license.\n\n/** Welcome to Deno!\n *\n * @module\n */\n\nconsole.log(\"Welcome to Deno!\");\n"
```

命令成功运行了！现在我们可以把文件名作为命令行参数传递给我们的运行时。

## 支持 TypeScript

如果我们想支持 TypeScript 和 TSX 要怎么做呢？

首先，我们要把 TypeScript 编译成 JavaScript。

我们把 `example.js` 重命名为 `example.ts` ，添加一些简单的 TS 代码：

```typescript
console.log("Hello", "runjs!");

interface Foo {
  bar: string;
  fizz: number;
}
let content: string;
content = await runjs.fetch(
  "https://deno.land/std@0.177.0/examples/welcome.ts"
);
console.log("Content from fetch", content);
```

接下来，我们需要更新 `main.rs` 中的模块加载器。目前我们使用的[模块加载器](https://github.com/denoland/roll-your-own-javascript-runtime/blob/10be000292c17b1e66391cbac0aa77ff6a5a97fc/src/main.rs#LL33-L36C29)是[`deno_core::FsModuleLoader`](https://docs.rs/deno_core/latest/deno_core/struct.FsModuleLoader.html)，它提供了从本地文件系统中加载模块的能力。然而，它只能加载 JS 文件。

```rust
// main.rs
// …

  let mut js_runtime = deno_core::JsRuntime::new(deno_core::RuntimeOptions {
    module_loader: Some(Rc::new(deno_core::FsModuleLoader)),
    extensions: vec![runjs_extension],
    ..Default::default()

// …
```

那么，让我们自己实现一个新的 `TsModuleLoader`，它可以根据文件扩展名来决定编译哪种文件。这个新的模块加载器需要实现 `deno_core::ModuleLoader` 这个 trait，所以我们需要实现 `resolve` 和 `load` 函数。

`resolve` 函数非常简单，我们只需要调用 `deno_core::resolve_import`。

```rust
// main.rs

struct TsModuleLoader;

impl deno_core::ModuleLoader for TsModuleLoader {
  fn resolve(
    &self,
    specifier: &str,
    referrer: &str,
    _kind: deno_core::ResolutionKind,
  ) -> Result<deno_core::ModuleSpecifier, deno_core::error::AnyError> {
    deno_core::resolve_import(specifier, referrer).map_err(|e| e.into())
  }
}
```

接下来，我们需要实现 `load` 函数。这比较复杂，因为将 TypeScript 编译为 JavaScript 并不简单 —— 你需要能够解析 TS 文件，创建 AST（抽象语法树），然后把 JavaScript 不能理解的类型相关代码去除，最后再把 AST 转化为 JS 代码。

我们不打算自己实现这些功能（这可能会花上数周的时间），而是直接使用 Deno 生态系统中现成的解决方案：[`deno_ast`](https://crates.io/crates/deno_ast)。

让我们通过命令行把它添加到依赖中：

```
$ cargo add deno_ast
```

在 `Cargo.toml` 中，我们需要把 `deno_ast`的 `transpile` feature 进行添加：

```toml
// …
[dependencies]
deno_ast = { version = "0.24.0", features = ["transpiling"] }
// …
```

接下来，我们添加四条 `use` 声明到 `main.rs` 的顶部，这些会在 `load` 函数中用到：

```rust
// main.rs

use deno_ast::MediaType;
use deno_ast::ParseParams;
use deno_ast::SourceTextInfo;
use deno_core::futures::FutureExt;

// …
```

现在我们可以来着手实现 `load` 函数了：

```rust
// main.rs

struct TsModuleLoader;

impl deno_core::ModuleLoader for TsModuleLoader {
  // fn resolve() ...

  fn load(
    &self,
    module_specifier: &deno_core::ModuleSpecifier,
    _maybe_referrer: Option<deno_core::ModuleSpecifier>,
    _is_dyn_import: bool,
  ) -> std::pin::Pin<Box<deno_core::ModuleSourceFuture>> {
    let module_specifier = module_specifier.clone();
    async move {
      let path = module_specifier.to_file_path().unwrap();

      // Determine what the MediaType is (this is done based on the file
      // extension) and whether transpiling is required.
      let media_type = MediaType::from(&path);
      let (module_type, should_transpile) = match MediaType::from(&path) {
        MediaType::JavaScript | MediaType::Mjs | MediaType::Cjs => {
          (deno_core::ModuleType::JavaScript, false)
        }
        MediaType::Jsx => (deno_core::ModuleType::JavaScript, true),
        MediaType::TypeScript
        | MediaType::Mts
        | MediaType::Cts
        | MediaType::Dts
        | MediaType::Dmts
        | MediaType::Dcts
        | MediaType::Tsx => (deno_core::ModuleType::JavaScript, true),
        MediaType::Json => (deno_core::ModuleType::Json, false),
        _ => panic!("Unknown extension {:?}", path.extension()),
      };

      // Read the file, transpile if necessary.
      let code = std::fs::read_to_string(&path)?;
      let code = if should_transpile {
        let parsed = deno_ast::parse_module(ParseParams {
          specifier: module_specifier.to_string(),
          text_info: SourceTextInfo::from_string(code),
          media_type,
          capture_tokens: false,
          scope_analysis: false,
          maybe_syntax: None,
        })?;
        parsed.transpile(&Default::default())?.text
      } else {
        code
      };

      // Load and return module.
      let module = deno_core::ModuleSource {
        code: code.into_bytes().into_boxed_slice(),
        module_type,
        module_url_specified: module_specifier.to_string(),
        module_url_found: module_specifier.to_string(),
      };
      Ok(module)
    }
    .boxed_local()
  }
}
```

我们来拆解一下这段代码。`load` 函数接受一个文件路径作为参数，返回一个 JavaScipt 模块。这个文件路径可以指向一个 JavaScript 文件或 TypeScript 文件，只要它能够被编译成一个 JavaScript 模块。

首先我们获取代码文件的真实路径，确定其 `MediaType` 以及是否需要进行转译。随后，我们把文件内容读取至一个字符串中，并在有必要的情况下对其进行转译。最后，这份代码文件会被转化为一个 `module` 并返回。

接下来，我们需要在创建 `JsRUntime` 的地方把原本的 `FsModuleLoader` 替换为新创建的 `TsModuleLoader`：

```rust
// …

  let mut js_runtime = deno_core::JsRuntime::new(deno_core::RuntimeOptions {
//  module_loader: Some(Rc::new(deno_core::FsModuleLoader)),
    module_loader: Some(Rc::new(TsModuleLoader)),
    extensions: vec![runjs_extension],
    ..Default::default()

// …
```

这样我们就可以让 TypeScript 文件顺利编译了！

让我们运行 `cargo run example.ts` 来看看效果：

```
cargo run example.ts
    Finished dev [unoptimized + debuginfo] target(s) in 0.73s
     Running `target/debug/runjs example.ts`
[out]: "Hello" "runjs!"
[out]: "Content from fetch" "// Copyright 2018-2023 the Deno authors. All rights reserved. MIT license.\n\n/** Welcome to Deno!\n *\n * @module\n */\n\nconsole.log(\"Welcome to Deno!\");\n"
```

通过 133 行 Rust 代码，我们就能够实现运行时对 TypeScript，TSX 的编译支持，以及其他丰富的功能和 API。

## 下一步？

将 JavaScript 和 TypeScript 嵌入 Rust 是搭建**高性能富交互应用**的一种很好的方法。不管是用于作为扩展你的平台功能的插件系统，或是构建高性能的专用运行时，Deno 都能让 JavaScript、TypeScript 和 Rust 之间的交互更加简单。
