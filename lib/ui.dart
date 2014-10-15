library giton.ui;

import 'dart:async';

import 'package:curses/curses.dart';
import 'package:logging/logging.dart';

export 'package:curses/curses.dart' show Point, Size, Key;

final keyboard = new Keyboard._(stdscr);

final Logger _log = new Logger('ui');
ScreenDC _screen;

ScreenDC get screen {
  if (_screen == null) {
    _screen = new ScreenDC._(stdscr);
    stdscr.setup(autoRefresh: true, cursorVisibility: CursorVisibility.INVISIBLE, escDelay: 25);
  }

  return _screen;
}

class KeyEvent {

  final Key key;

  KeyEvent(this.key);

}

class DC {

  final Window _window;
  final size;
  final clientSize;
  bool _border;

  DC._(Window window, this._border) :
    _window = window,
    size = window.getmaxyx(),
    clientSize = new Size(window.getmaxyx().rows-2, window.getmaxyx().columns-2) {

    _log.fine('DC._: window=${window}');
    clear();
  }

  String toString() => 'DC(${_window})';

  void clear() {
    _log.fine('clear: this=${this}');
    _window.clear();
    _drawBorder();
  }

  void drawString(Point location, String msg) {
    _window.addstr(msg, location: location);
  }

  void dispose({bool clear: true}) {
    _window.dispose(clear: clear);
  }

  void _drawBorder() {
    if (_border) {
      _window.border();
    }
  }

}

class ScreenDC extends DC {

  ScreenDC._(Screen screen) : super._(screen, true);

  DC createWindow(Point location, Size size, {bool border: true}) =>
      new DC._(new Window(location, size), border);

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
      //_log.fine("=====> ${new Key('BACKSPACE')}");
      _log.fine('_getKey: key=${key}');
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
