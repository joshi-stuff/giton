part of giton.vi3;

final Logger _log = new Logger('vi3');

void launch(App app) {
  Logger.root.onRecord.listen((LogRecord rec) {
    new File(
        "app.log").writeAsStringSync(
            '${rec.level.name}: ${rec.loggerName}: ${rec.message}\n',
            mode: FileMode.APPEND);
  });

  runZoned(() {
    try {
      app._run();
    } catch (err, stackTrace) {
      _handleError(err, stackTrace);
    }
  }, onError: (err, stackTrace) {
    _handleError(err, stackTrace);
  });
}

void _handleError(err, stackTrace) {
  screen.dispose();
  print(err);
  print(stackTrace);
  exit(1);
}

typedef View ViewFactory(ViewStack viewStack);
typedef void KeyCaptureHandler(KeyEvent ev);

class App {

  final _screenDC = screen;
  final _keyCaptureHandlers = <KeyCaptureHandler>[];
  final _commands = new CommandRegistry();
  final _storedKeys = <Key>[];
  final _viewStacks = <ViewStack>[];
  final ViewFactory _initialViewFactory;
  ViewStack _selectedViewStack;

  App(this._initialViewFactory) {
    addCommand(new Command([new Key('h')], 'h', 'Help', doHelp));
    addCommand(new Command([new Key('q')], 'q', 'Quit', doQuit));
    addCommand(new Command([new Key(' ')], ' ', 'Open OmniCommand (TM)', doOpenOmniCommand, hidden: true));
    addCommand(new GoBackCommand(doGoBack));
  }

  ViewStack get selectedViewStack => _selectedViewStack;
  View get selectedView => (_selectedViewStack == null) ? null : _selectedViewStack.selectedView;
  Size get screenSize => _screenDC.size;

  void addCommand(Command command) {
    _commands.add(command);
  }

  void selectViewStack(int index) {
    if ((index < _viewStacks.length) && (_viewStacks[index] == _selectedViewStack)) {
      return;
    }

    while (_viewStacks.length <= index) {
      _viewStacks.add(null);
    }

    if (_viewStacks[index] == null) {
      _viewStacks.insert(index, _createViewStack(index));
    }

    if (_selectedViewStack != null) {
      selectedView.deactivate();
    }

    _selectedViewStack = _viewStacks[index];

    selectedView.activate();
  }

  void pushKeyCaptureHandler(KeyCaptureHandler keyCaptureHandler) {
    _keyCaptureHandlers.add(keyCaptureHandler);
    _storedKeys.clear();
  }

  KeyCaptureHandler popKeyCaptureHandler() {
    return _keyCaptureHandlers.removeLast();
  }

  // Command handlers
  void doGoBack() {
    selectedViewStack.pop();
  }

  void doHelp() {
    if (selectedView is! HelpView) {
      selectedViewStack.push(new HelpView(selectedViewStack));
    }
  }

  void doQuit() {
    screen.dispose();
    exit(0);
  }

  void doOpenOmniCommand() {
    // TODO: implement openOmniCommand
  }

  // Helper methods

  ViewStack _createViewStack(int index) {
    var viewStack = new ViewStack(this, index);
    viewStack.push(_initialViewFactory(viewStack));
    return viewStack;
  }

  void _onKeyEvent(KeyEvent ev) {
    if (_keyCaptureHandlers.isNotEmpty) {
      _keyCaptureHandlers.last(ev);
    } else {
      _storedKeys.add(ev.key);

      if ((_storedKeys.length == 1) && _storedKeys.last.name.startsWith('F')) {
        int fnum = int.parse(_storedKeys.last.name.substring(1), onError: (_) => null);

        if (fnum != null) {
          _log.fine('key event: selectViewStack(${fnum - 1})');
          _storedKeys.clear();
          selectViewStack(fnum-1);
        }
      } else {
        final cmds = _searchCommandsKeys(_storedKeys);

        switch (cmds.length) {
          case 0:
            _log.fine('key event: _storedKeys.clear()');
            _storedKeys.clear();
            break;

          case 1:
            final cmd = cmds[0];

            if (cmd.isForKeys(_storedKeys)) {
              _log.fine('key event: ${cmds[0]}.run()');
              _storedKeys.clear();
              cmds[0].run();
            } else {
              _log.fine('key event: _storedKeys=${_storedKeys}  cmds=${cmds}');
            }
            break;

          default:
            _log.fine('key event: _storedKeys=${_storedKeys}  cmds=${cmds}');
            break;
        }
      }

      selectedView.repaint();
    }
  }

  void _run() {
    _viewStacks.add(_createViewStack(0));
    _selectedViewStack = null;
    selectViewStack(0);

    keyboard.stream.listen(_onKeyEvent);
  }

  // Command methods
  List<Command> _getCommands() {
    var commands = _selectedViewStack._getCommands();
    commands.addAll(_commands.all);
    return commands;
  }

  List<Command> _searchCommandsPattern(String pattern) {
    var commands = _selectedViewStack._searchCommandsPattern(pattern);
    commands.addAll(_commands.searchPattern(pattern));
    return commands;
  }

  List<Command> _searchCommandsKeys(List<Key> keys) {
    var commands = _selectedViewStack._searchCommandsKeys(keys);

    commands.addAll(_commands.searchKeys(keys));

    return commands;
  }

/*
    def run_command(self):
        x = self.screen_size.x // 8
        y = self.screen_size.y // 3 - 1
        w = 6 * self.screen_size.x // 8
        h = 3

        helpmsg = "(search for command; try help)"

        box = newwin(h, w, y, x)
        box.border()
        box.addstr(1, 1, '_', Color.WHITE | A_BLINK | A_UNDERLINE)
        box.addstr(1, w - len(helpmsg) - 1, helpmsg, Color.YELLOW)
        box.refresh()

        cbox = newwin(14, w, y+3, x)

        pattern = ''
        commands = []
        selected_command_index = -1

        while True:
            key = self.screen.getkey()

            if key == '\x7f':  # Backspace
                pattern = pattern[:-1]

            elif key == '\x1b':  # Esc
                break

            elif key == 'KEY_UP':
                selected_command_index -= 1
                if selected_command_index == -1:
                    selected_command_index = 0

            elif key == 'KEY_DOWN':
                selected_command_index += 1
                if selected_command_index >= len(commands):
                    selected_command_index = len(commands) - 1

            elif key == '\n':

                break

            else:
                # if len(key)==1:
                pattern += key
                selected_command_index = -1

            box.clear()
            box.border()

            if len(pattern) == 0:
                box.addstr(1, w - len(helpmsg) - 1, helpmsg, Color.YELLOW)
                box.addstr(1, 1, '_', Color.WHITE | A_BLINK | A_UNDERLINE)

            else:
                box.addnstr(1, 1, pattern[-w+3:], w-2, Color.WHITE)
                box.addstr(1, min(len(pattern)+1, w-2), '_',
                           Color.WHITE | A_BLINK | A_UNDERLINE)

            commands = []

            if len(pattern) > 0:
                commands = self.search_commands(pattern)

            if (len(commands) > 0) and (selected_command_index == -1):
                selected_command_index = 0

            cbox.clear()
            cbox.border()

            for i, command in enumerate(commands):
                text = '[' + command.shortcut + '] ' + command.name
                if i == selected_command_index:
                    cbox.addnstr(i+1, 1, text, w-2, Color.YELLOW | A_REVERSE)
                else:
                    cbox.addnstr(i+1, 1, text, w-2, Color.YELLOW)

            box.refresh()
            cbox.refresh()

        box.erase()
        cbox.erase()

        box.refresh()
        cbox.refresh()

        if selected_command_index != -1:
            commands[selected_command_index].run()
 */
}

class ViewStack {

  final App app;
  final int index;
  final _commands = new CommandRegistry();
  final _views = <View>[];

  ViewStack(this.app, this.index);

  Iterable<View> get views => _views;
  View get selectedView => _views.last;

  void addCommand(Command command) {
    _commands.add(command);
  }

  void push(View view) {
    _deactivateSelectedView();
    _views.add(view);
    _activateSelectedView();
  }

  void pop() {
    if (_views.length > 1) {
      _deactivateSelectedView();
      _views.removeLast();
      _activateSelectedView();
    }
  }

  void replaceAll(View view) {
    if (_views.length > 0) {
      selectedView.deactivate();
    }

    _views.clear();
    _views.add(view);

    selectedView.activate();
  }

  void _activateSelectedView() {
    if ((app.selectedViewStack == this) && (_views.length > 0)) {
      selectedView.activate();
    }
  }

  void _deactivateSelectedView() {
    if ((app.selectedViewStack == this) && (_views.length > 0)) {
      selectedView.deactivate();
    }
  }

  // Command methods

  List<Command> _getCommands() {
    var commands = _views.last._getCommands();
    commands.addAll(_commands.all);
    return commands;
  }

  List<Command> _searchCommandsPattern(String pattern) {
    var commands = _views.last._searchCommandsPattern(pattern);
    commands.addAll(_commands.searchPattern(pattern));
    return commands;
  }

  List<Command> _searchCommandsKeys(List<Key> keys) {
    var commands = _views.last._searchCommandsKeys(keys);

    commands.addAll(_commands.searchKeys(keys));

    return commands;
  }

}

class View {

  final ViewStack viewStack;
  final _commands = new CommandRegistry();
  DC _dc;
  Point _location;
  Size _size;
  String _title = '';
  String _status = '';

  View(this.viewStack) {
    _size = app._screenDC.size;
    _location = new Point(0, 0);
  }

  App get app => viewStack.app;
  Point get location => _location;
  Size get size => _size;

  void set location(Point location) {
    _location = location;
    _disposeDC();
  }

  void set size(Size size) {
    _size = size;
    _disposeDC();
  }

  void set title(String title) {
    _title = title;
  }

  void set status(String status) {
    _status = status;
  }

  void addCommand(Command command) {
    _commands.add(command);
  }

  void repaint() {
    if (_dc == null) {
      _dc = app._screenDC.createWindow(_location, _size);
      _log.fine('repaint: new dc=${_dc}');
    }

    _log.fine('repaint: this=${this} dc=${_dc}');
    _dc.clear();
    _drawDecoration(_dc);

    _log.fine('paint: this=${this} dc=${_dc}');
    paint(_dc);
  }

  void paint(DC dc) {
  }

  void activate() {
    repaint();
  }

  void deactivate() {
  }

  void _disposeDC() {
    if (_dc != null) {
      _dc.dispose(clear: false);
      _dc = null;
    }
  }

  void _drawDecoration(DC dc) {
    _log.fine('_drawDecoration: this=${this} dc=${_dc}');

    if (_title.length > 0) {
      var location = new Point(0, 2);
      dc.drawString(location, ' ${_title} '); // Color.WHITE);
    }

    if (_status.length > 0) {
      var location = new Point(size.rows - 1, size.columns - _status.length - 4);
      dc.drawString(location, ' ${_status} '); // Color.YELLOW);
    }
  }

  // Command methods

  List<Command> _getCommands() => _commands.all.toList();

  List<Command> _searchCommandsPattern(String pattern) => _commands.searchPattern(pattern);

  List<Command> _searchCommandsKeys(List<Key> keys) => _commands.searchKeys(keys);

}

class HelpView extends View {

  static final _HELP_MSG_CLOSE = '(press ESC to close)';
  static final _HELP_MSG_AVAILABLE_COMMANDS = 'Available commands';

  HelpView(ViewStack viewStack) : super(viewStack) {
    final screenSize = app.screenSize;

    location = new Point(screenSize.rows ~/ 8, screenSize.columns ~/ 8);
    size = new Size(6 * screenSize.rows ~/ 8, 6 * screenSize.columns ~/ 8);
    title = _HELP_MSG_AVAILABLE_COMMANDS;
    status = _HELP_MSG_CLOSE;
  }

  void paint(DC dc) {
    final commands = app._getCommands();
    int row = 2;
    for (var i = 0; i < commands.length; i++) {
      final command = commands[i];
      if (!command.hidden) {
        final location = new Point(row++, 3);
        dc.drawString(location, '[' + command.shortcut + '] ' + command.name);
      }
    }
  }

}
