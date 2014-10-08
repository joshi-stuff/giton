part of giton.vi3;

void launch(App app) {
  Logger.root.level = Level.ALL;
  Logger.root.onRecord.listen((LogRecord rec) {
    new File(
        "app.log").writeAsStringSync(
            '${rec.level.name}: ${rec.time}: ${rec.message}\n',
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

  static final _HELP_MSG_CLOSE = '(press ESC to close)';
  static final _HELP_MSG_AVAILABLE_COMMANDS = 'Available commands:';

  final _dc = screen;
  final _keyCaptureHandlers = <KeyCaptureHandler>[];
  final _commands = new CommandRegistry();
  final _viewStacks = <ViewStack>[];
  final ViewFactory _initialViewFactory;
  ViewStack _selectedViewStack;

  App(this._initialViewFactory) {
    addCommand(new Command([new Key('h')], 'h', 'Help', doHelp));
    addCommand(new Command([new Key('q')], 'q', 'Quit', doQuit));
    addCommand(new Command([new Key(' ')], ' ', 'Open OmniCommand (TM)', doOpenOmniCommand, hidden: true));
  }

  ViewStack get selectedViewStack => _selectedViewStack;
  View get selectedView => (_selectedViewStack == null) ? null : _selectedViewStack.selectedView;

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
  }

  KeyCaptureHandler popKeyCaptureHandler() {
    return _keyCaptureHandlers.removeLast();
  }

  // Command handlers

  void doHelp() {
    /* TODO: make event driven
    final boxLocation = new Point(_dc.size.rows ~/ 8, _dc.size.columns ~/ 8);
    final boxSize = new Size(6 * _dc.size.rows ~/ 8, 6 * _dc.size.columns ~/ 8);
    final msgCloseLocation =
        new Point(boxSize.rows - 2, boxSize.columns - _HELP_MSG_CLOSE.length - 1);
    final msgAvailableCommandsLocation = new Point(2, 3);

    final box = new Window(boxLocation, boxSize);
    box.border();

    box.addstr(_HELP_MSG_CLOSE, location: msgCloseLocation, colorPair: Color.YELLOW);
    box.addstr(
        _HELP_MSG_AVAILABLE_COMMANDS,
        location: msgAvailableCommandsLocation,
        colorPair: Color.WHITE);

    final commands = _getCommands();
    for (var i = 0; i < commands.length; i++) {
      final command = commands[i];
      final location = new Point(i + 4, 7);

      box.addstr('[' + command.shortcut + '] ' + command.name, location: location);
    }

    _screen.getkey().then((key) {
      box.dispose();
    });
    */
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
      final key = ev.key;

      final cmds = _searchCommandsKeys([key]);
      _log.fine('key event: "${key}"  candidate commands: ${cmds}');

      if (cmds.length == 0) {
      } else if (cmds.length == 1) {
        cmds[0].run();
      } else {

      } else if (key.name.startsWith('F')) {
        int fnum = int.parse(key.name.substring(1), onError: (_) => null);

        if (fnum != null) {
          _log.fine('selecting view stack: ${fnum - 1}');
          selectViewStack(fnum-1);
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
    if (_views.length > 0) {
      selectedView.deactivate();
    }

    _views.add(view);

    selectedView.activate();
  }

  void pop() {
    if (_views.length > 1) {
      selectedView.deactivate();
      _views.removeLast();
      selectedView.activate();
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

  // Command methods

  List<Command> _getCommands() {
    var commands = _views.last._getCommands();
    commands.addAll(_commands.all);
    return commands;
  }

  List<Command> _searchCommandsPattern(String pattern) {
    var commands = _views.last._searchCommands(pattern);
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

  View(this.viewStack) {
    _dc = app._dc;
  }

  App get app => viewStack.app;

  void addCommand(Command command) {
    _commands.add(command);
  }

  void repaint() {
    _dc.clear();
    paint(_dc);
  }

  void paint(DC dc) {
  }

  void activate() {
    repaint();
  }

  void deactivate() {
  }

  // Command methods

  List<Command> _getCommands() => _commands.all.toList();

  List<Command> _searchCommandsPatter(String pattern) => _commands.searchPattern(pattern);

  List<Command> _searchCommandsKeys(List<Key> key) => _commands.searchKeys([key]);

}
