import 'dart:ffi';
import 'dart:io';

/// Check the native engine that source extensions load on Linux before shipping.
void main(List<String> args) {
  final bundle = Directory(
    args.isEmpty ? 'build/linux/x64/release/bundle' : args.single,
  ).absolute.path;
  final path = '$bundle/lib/libquickjs_c_bridge_plugin.so';
  try {
    final quickjs = DynamicLibrary.open(path);
    for (final symbol in ['jsNewRuntime', 'jsNewContext', 'jsEval']) {
      quickjs.lookup<Void>(symbol);
    }
    stdout.writeln('Bundled QuickJS library loads successfully: $path');
  } catch (error) {
    stderr.writeln('Cannot load the bundled QuickJS engine: $error');
    exitCode = 1;
  }
}
