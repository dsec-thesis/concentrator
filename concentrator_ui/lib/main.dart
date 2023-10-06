import 'dart:io';

import 'package:flutter/material.dart';
import 'package:get/get_state_manager/get_state_manager.dart';
import 'package:get/instance_manager.dart';
import 'package:get/route_manager.dart';
import 'package:uuid/uuid.dart';

void main() {
  runApp(MyApp());
}

class LoraAntennaConfig {
  int frequency = 0;
  int spreadingFactor = 0;
  int bandwidth = 0;
  int codingRate = 0;
  int preambleLength = 0;
  bool crcEnable = false;
  int syncWord = 0;
}

class LoraConfig {
  LoraAntennaConfig rx = LoraAntennaConfig();
  LoraAntennaConfig tx = LoraAntennaConfig();
}

class ClientConfig {
  String clientId = "";
  String clientSecret = "";
  String tokenUrl = "";
  String tokenFile = "";
  String apiUrl = "";
  String parkinglotId = "";
}

class WifiConfig {
  String ssid = "";
  String password = "";
}

class ConfiguracionNodo {
  LoraConfig loraConfig = LoraConfig();
  ClientConfig clientConfig = ClientConfig();
  WifiConfig wifiConfig = WifiConfig();
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      debugShowCheckedModeBanner: false,
      home: ConfiguracionNodoScreen(),
    );
  }
}

class ConfiguracionNodoScreen extends StatefulWidget {
  @override
  _ConfiguracionNodoScreenState createState() =>
      _ConfiguracionNodoScreenState();
}

class _ConfiguracionNodoScreenState extends State<ConfiguracionNodoScreen> {
  ConfiguracionNodo configuracionNodo = ConfiguracionNodo();
  int currentStep = 0;
  List<WifiNetwork> availableNetworks = [
    WifiNetwork(ssid: 'patriciothecat'),
    WifiNetwork(ssid: 'GoldelSiglo'),
    WifiNetwork(ssid: 'FRANYNICO'),
    WifiNetwork(ssid: 'Personal Wifi Zone'),
    WifiNetwork(ssid: 'Maria 2.4G'),
    WifiNetwork(ssid: 'Maria 5G'),
    WifiNetwork(ssid: 'Celina'),
    WifiNetwork(ssid: 'Personal Wifi Zone'),
    WifiNetwork(ssid: 'GoldelSiglo'),
    WifiNetwork(ssid: 'Mateo'),
    WifiNetwork(ssid: 'JorPaganini 2.4'),
    WifiNetwork(ssid: 'Chela'),
    WifiNetwork(ssid: 'Personal Wifi Zone'),
    WifiNetwork(ssid: 'LOS LEPROSOS'),
    WifiNetwork(ssid: 'ClaroWifi24G'),
    WifiNetwork(ssid: 'Personal Wifi Zone'),
    WifiNetwork(ssid: 'Irene 5.8'),
    WifiNetwork(ssid: 'Irene'),
    WifiNetwork(ssid: 'Fibertel WiFi129 5.8GHz'),
    WifiNetwork(ssid: 'Fibertel WiFi129 2.4GHz'),
    WifiNetwork(ssid: 'VICTORIA 5.8'),
    WifiNetwork(ssid: 'Jesus'),
    WifiNetwork(ssid: 'Thot-5G'),
    WifiNetwork(ssid: 'DiegoSarina'),
    WifiNetwork(ssid: 'DiegoSarina5Ghz'),
  ];

  final concentratorIdKey = GlobalKey<FormState>();
  final parkingLotIdKey = GlobalKey<FormState>();

  late final TextEditingController concentratorIdController;
  late final TextEditingController parkingLotIdController;

  var concentratorId;
  var parkingLotId;

  bool isConnecting = false;

  @override
  void initState() {
    super.initState();

    concentratorId = Uuid().v4();
    parkingLotId = Uuid().v4();

    // Inicializar los controladores con los valores predeterminados
    concentratorIdController = TextEditingController(text: concentratorId);
    parkingLotIdController = TextEditingController(text: parkingLotId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Nodo Concentrador - Configuración'),
      ),
      body: currentStep == 0
          ? _buildWelcomeStep()
          : currentStep == 1
              ? _buildWifiStep()
              : _buildAwsCredentialsStep(),
    );
  }

  Widget _buildWelcomeStep() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            textAlign: TextAlign.center,
            'Bienvenido al proceso de configuración',
            style: TextStyle(fontSize: 20),
          ),
          SizedBox(height: 20),
          Text(
            'Este proceso te guiará para configurar el nodo.',
            style: TextStyle(fontSize: 16),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 40),
          ElevatedButton(
            onPressed: () {
              setState(() {
                currentStep++;
              });
            },
            child: Text('Continuar'),
          ),
          SizedBox(height: 20),
          TextButton(
            onPressed: () {
              // Maneja la cancelación según tus necesidades
            },
            child: Text('Cancelar'),
          ),
        ],
      ),
    );
  }

  Widget _buildWifiStep() {
    return Column(
      children: [
        Text(
          'Paso 1: Configuración WiFi',
          style: TextStyle(fontSize: 20),
        ),
        SizedBox(height: 20),
        Text(
          'Selecciona una red WiFi y proporciona la contraseña:',
          style: TextStyle(fontSize: 16),
        ),
        SizedBox(height: 20),
        DropdownButtonFormField<WifiNetwork>(
          value: availableNetworks.isNotEmpty ? availableNetworks[0] : null,
          onChanged: (value) {
            setState(() {
              configuracionNodo.wifiConfig.ssid = value!.ssid;
            });
          },
          items: availableNetworks.map((network) {
            return DropdownMenuItem<WifiNetwork>(
              value: network,
              child: Text(network.ssid),
            );
          }).toList(),
        ),
        SizedBox(height: 20),
        TextFormField(
          decoration: InputDecoration(
            labelText: 'Contraseña',
            suffixIcon: IconButton(
              icon: Icon(
                Icons.visibility,
                color: Colors.grey,
              ),
              onPressed: () {
                // Toggle the visibility of the password field
                setState(() {
                  _isPasswordVisible = !_isPasswordVisible;
                });
              },
            ),
          ),
          obscureText: !_isPasswordVisible,
          onChanged: (value) {
            configuracionNodo.wifiConfig.password = value;
          },
        ),
        SizedBox(height: 20),
        ElevatedButton(
          onPressed: () {
            // Simular una espera antes de avanzar
            setState(() {
              isConnecting = true;
            });
            Future.delayed(Duration(seconds: 2), () {
              setState(() {
                currentStep++;
                isConnecting = false;
              });
            });
          },
          child: isConnecting
              ? CircularProgressIndicator() // Mostrar un indicador de progreso durante la conexión
              : Text('Conectar'),
        ),
        SizedBox(height: 20),
        TextButton(
          onPressed: () {
            setState(() {
              currentStep--;
            });
          },
          child: Text('Volver Atrás'),
        ),
      ],
    );
  }

  Widget _buildAwsCredentialsStep() {
    String concentrator = Uuid().v4();
    String parkingLotId = Uuid().v4();
    setState(() {});
    return Center(
      child: Column(
        children: [
          SizedBox(
            height: 10,
          ),
          Text(
            textAlign: TextAlign.center,
            'Paso 2: Credenciales generadas',
            style: TextStyle(fontSize: 20),
          ),
          // SizedBox(height: 20),
          // Text(
          //   'Confirma la información del estacionamiento:',
          //   style: TextStyle(fontSize: 16),
          // ),
          SizedBox(height: 20),
          Text(
            'Concentrator ID: ${concentrator}',
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 20),
          Text(
            'Parking Lot ID: ${parkingLotId}',
            style: TextStyle(fontSize: 16),
          ),
          SizedBox(height: 50),
          ElevatedButton(
            onPressed: () {
              // Mostrar un mensaje de confirmación antes de guardar
              showDialog(
                context: context,
                builder: (context) {
                  return AlertDialog(
                    title: Text('Confirmar Configuración'),
                    content: Text('¿Deseas guardar esta información?'),
                    actions: [
                      TextButton(
                        onPressed: () {
                          // Guardar la información aquí
                          // configuracionNodo.clientConfig.clientId y configuracionNodo.clientConfig.clientSecret contienen los valores predeterminados
                          Get.offAll(() => ExitScreen()); // Cerrar el diálogo
                        },
                        child: Text('Guardar'),
                      ),
                      TextButton(
                        onPressed: () {
                          Navigator.of(context).pop(); // Cerrar el diálogo
                        },
                        child: Text('Cancelar'),
                      ),
                    ],
                  );
                },
              );
            },
            child: Text('Guardar Información'),
          ),
          SizedBox(height: 20),
          TextButton(
            onPressed: () {
              setState(() {
                currentStep--;
              });
            },
            child: Text('Volver Atrás'),
          ),
        ],
      ),
    );
  }

  bool _isPasswordVisible = false;
}

class WifiNetwork {
  final String ssid;

  WifiNetwork({required this.ssid});
}

class ExitScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Salir del Sistema'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              textAlign: TextAlign.center,
              'Usted ha completado el proceso de configuracion de su nodo concetrador',
              style: TextStyle(fontSize: 15),
            ),
            SizedBox(height: 20),
            Text(
              'El mismo ya se encuentra listo para comenzar a recibir informacion de los nodos sensores',
              style: TextStyle(fontSize: 13),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 40),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text('SALIR'),
            ),
            // SizedBox(height: 20),
            // TextButton(
            //   onPressed: () {
            //     // Maneja la cancelación según tus necesidades
            //   },
            //   child: Text('Cancelar'),
            // ),
          ],
        ),
      ),
    );
  }
}
