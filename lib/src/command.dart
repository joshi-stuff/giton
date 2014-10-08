part of giton.vi3;

class CommandRegistry {

  final _commands = <Command>[];

  CommandRegistry();

  void add(Command command) {
    _commands.add(command);
  }

  Iterable<Command> get all => _commands;

  List<Command> searchPattern(String pattern) {
    var commands = <Command>[];

    _commands.forEach((command) {
      if (command.name.toLowerCase().startsWith(pattern.toLowerCase())) {
        commands.add(command);
      }
    });

    _commands.forEach((command) {
      if (command.name.toLowerCase().contains(pattern.toLowerCase()) &&
          !commands.contains(command)) {
        commands.add(command);
      }
    });

    return commands;
  }

  List<Command> searchKeys(List<Key> keys) {
    var commands = <Command>[];

    _commands.forEach((command) {
      var ckeys = command.keys;

      if ((ckeys.length >= keys.length) && (_equals(ckeys, keys.sublist(0, ckeys.length)))) {
        commands.add(command);
      }
    });

    return commands;
  }

  bool _equals(List<Key> ckeys, List<Key> keys) {
    for (int i = 0; i < ckeys.length; i++) {
      if (keys[i] != ckeys[i]) {
        return false;
      }
    }

    return true;
  }

}

class Command {

  final List<Key> keys;
  final String shortcut;
  final String name;
  final bool hidden;
  final Function _handler;

  Command(this.keys, this.shortcut, this.name, this._handler, {this.hidden: false});

  void run() {
    _handler();
  }

  String toString() => 'Command(${name})';

}

class GoBackCommand extends Command {
  GoBackCommand(Function handler)
      : super([new Key('BACKSPACE')], 'Backspace', 'Go back', handler, hidden: true);
}

class OpenSelectionCommand extends Command {
  OpenSelectionCommand(Function handler)
      : super([new Key('ENTER')], 'Enter', 'Open selection', handler, hidden: true);
}

class GoUpCommand extends Command {
  GoUpCommand(Function handler) : super([new Key('UP')], 'Up', 'Go up', handler, hidden: true);
}

class GoDownCommand extends Command {
  GoDownCommand(Function handler) : super([new Key('DOWN')], 'Down', 'Go down', handler, hidden: true);
}

class GoLeftCommand extends Command {
  GoLeftCommand(Function handler) : super([new Key('LEFT')], 'Left', 'Go left', handler, hidden: true);
}

class GoRightCommand extends Command {
  GoRightCommand(Function handler) : super([new Key('RIGHT')], 'Right', 'Go right', handler, hidden: true);
}

class PageUpCommand extends Command {
  PageUpCommand(Function handler) : super([new Key('PPAGE')], 'Page Up', 'Page up', handler, hidden: true);
}

class PageDownCommand extends Command {
  PageDownCommand(Function handler)
      : super([new Key('NPAGE')], 'Page Down', 'Page down', handler, hidden: true);
}

class GoToStartCommand extends Command {
  GoToStartCommand(Function handler)
      : super([new Key('g'), new Key('g')], 'gg', 'Go to start', handler, hidden: true);
}

class GoToEndCommand extends Command {
  GoToEndCommand(Function handler)
      : super([new Key('G')], 'G', 'Go to end', handler, hidden: true);
}








