
import 'dart:io';

import 'package:giton/ui.dart';


void main() {
  screen.drawString(new Point(1, 1), 'hola');

  var win = screen.createWindow(new Point(10, 10), new Size(20, 20));
  win.drawString(new Point(1, 1), 'aaa');


  keyboard.stream.listen((_){
    screen.dispose();
    exit(0);
  });
}