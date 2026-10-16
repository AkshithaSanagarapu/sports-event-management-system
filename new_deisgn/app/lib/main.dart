import 'package:flutter/material.dart';
import 'package:flutter_webview_pro/platform_interface.dart';
import 'package:flutter_webview_pro/webview_flutter.dart';

class Palette {
  MaterialColor mycolor = MaterialColor(
    Color.fromARGB(255, 0, 128, 0).value,
    <int, Color>{
      50: Color.fromRGBO(0, 137, 123, 0.1),
      100: Color.fromRGBO(0, 137, 123, 0.2),
      200: Color.fromRGBO(0, 137, 123, 0.3),
      300: Color.fromRGBO(0, 137, 123, 0.4),
      400: Color.fromRGBO(0, 137, 123, 0.5),
      500: Color.fromRGBO(0, 137, 123, 0.6),
      600: Color.fromRGBO(0, 137, 123, 0.7),
      700: Color.fromRGBO(0, 137, 123, 0.8),
      800: Color.fromRGBO(0, 137, 123, 0.9),
      900: Color.fromARGB(255, 0, 137, 48),
    },
  );
}

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // title: '',
      theme: ThemeData(
        primarySwatch: Palette().mycolor,
      ),
      home: MyWebView(),
    );
  }
}

class MyWebView extends StatefulWidget {
  @override
  _MyWebViewState createState() => _MyWebViewState();
}

class _MyWebViewState extends State<MyWebView> {
  late WebViewController _webViewcontroller;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
          // title: Text(''),
          ),
      body: WillPopScope(
        onWillPop: () async {
          if (await _webViewcontroller.canGoBack()) {
            _webViewcontroller.goBack();
            return false;
          } else {
            return true;
          }
        },
        child: WebView(
          // initialUrl: "http://192.168.1.6:5000",
          initialUrl: "http://10.0.2.2:5000",
          javascriptMode: JavascriptMode.unrestricted,
          onWebViewCreated: (WebViewController webViewController) {
            _webViewcontroller = webViewController;
          },
        ),
      ),
    );
  }
}
