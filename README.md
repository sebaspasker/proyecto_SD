### Funcionamiento

Para su correcto funcionamiento ejecutar (en orden):

```bash
# Desde el directorio base ./sd
source ../bin/activate

# Desde la carpeta de kafka
# En diferentes terminales
./bin/zookeeper-server-start.sh  config/zookeeper.properties
./bin/kafka-server-start.sh ./config/server.properties

# Desde el directorio base
# Scripts de creación 
python ./scripts/create_json_cfg.py # Opcional
python ./scripts/create_table_player.py
python ./scripts/create_weather_table.py # P2

python ./scripts/convert_sql_to_json.py # P3
python ./scripts/create_pem.py # P3 Opcional

# Editar config.json en caso de ser necesario
vim ./json/json.config

# Arrancamos los servidores secundarios (En terminales distintos)
python AA_Registry.py config/config.json
python AA_Weather.py config/config.json # NO se INCLUYE en la práctica 3
node api/index.js    # Se INCLUYE en la práctica 3

python AA_Engine.py config/config.json
python AA_Player.py config/config.json
```
