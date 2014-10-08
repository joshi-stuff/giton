library giton.ui;

import 'dart:async';

import 'package:curses/curses.dart';

export 'package:curses/curses.dart' show Point, Size, Key;

final keyboard = new Keyboard._(stdscr);

ScreenDC _screen;

ScreenDC get screen {
  if (_screen == null) {
    _screen = new ScreenDC._(stdscr);
    stdscr.setup(autoRefresh: true, cursorVisibility: CursorVisibility.INVISIBLE);
  }

  return _screen;
}

class KeyEvent {

  final Key key;

  KeyEvent(this.key);

}

class DC {

  final Window _window;

  DC(this._window);

  Size get size => _window.getmaxyx();

  void clear() {
    _window.clear();
  }

  void drawString(Point location, String msg) {
    _window.addstr(msg, location: location);
  }

}

class ScreenDC extends DC {

  ScreenDC._(Screen screen) : super(screen);

  void dispose() {
    stdscr.dispose(clear: true);
  }

}

class Keyboard {

  final Screen _screen;
  final _controller = new StreamController<KeyEvent>();

  Keyboard._(this._screen) {
    _getKey();
  }

  Stream get stream => _controller.stream;

  void _getKey() {
    _screen.wgetch().then((Key key) {
      _controller.add(new KeyEvent(key));
      _getKey();
    });
  }

}

class Style {

  static int _nextColorPair = 1;
  static final _styles = new Map<String, Style>();

  final String _name;
  final int _colorPair;
  final Color _foreground;
  final Color _background;
  final List<Attribute> _attributes;

  static void define(String name, Color foreground, Color background, [List<Attribute> attributes =
      const [
      ]]) {

    _styles[name] = new Style._(name, foreground, background, attributes);
  }

  factory Style(String name) {
    var style = _styles[name];

    if (style == null) {
      throw new ArgumentError("Undefined style: ${name}");
    }

    return style;
  }

  Style._(this._name, this._foreground, this._background, this._attributes)
      : _colorPair = _nextColorPair++ {

    stdscr.init_pair(_colorPair, _foreground, _background);
  }

}
