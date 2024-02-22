# Tidal Cyber API 

This is a tool generating MISP galaxies and clusters from Tidal Cyber API.

## Endpoints
https://app-api.tidalcyber.com/api/v1/technique

https://app-api.tidalcyber.com/api/v1/references

https://app-api.tidalcyber.com/api/v1/tactic

https://app-api.tidalcyber.com/api/v1/campaigns/

https://app-api.tidalcyber.com/api/v1/software/

https://app-api.tidalcyber.com/api/v1/groups/

## Configuration
The configuration file is located in `config.json` and maps the fields of the Tidal API to the Galaxy and Cluster fields. It consists of the following sections:
- `UUID`: The UUID of the galaxy to be created
- `GALAXY_CONFIGS`: The configuration of the galaxies to be created in the `galaxies` folder of the MISP-galaxy repository
  - `name`: The name of the galaxy
  - `namespace`: The namespace of the galaxy
  - `description`: The description of the galaxy
  - `type`: The type of the galaxy
  - `uuid`: The UUID of the galaxy (will be inserted from the `UUID` section)
- `CLUSTER_CONFIGS`: The configuration of the clusters to be created in the `clusters` folder of the MISP-galaxy repository 
  - `authors`: The authors of the cluster
  - `category`: The category of the cluster
  - `description`: The description of the cluster
  - `name`: The name of the cluster
  - `source`: The source of the cluster
  - `type`: The type of the cluster
  - `uuid`: The UUID of the cluster (will be inserted from the `UUID` section)
  - `values`: The values of the cluster (will be inserted from the `VALUE_FIELDS` section)
- `VALUE_FIELDS`: Defines the mapping of the fields in the Tidal Cyber API to the fields in the MISP cluster values array
  - `description`: The description of the cluster value
  - `meta`: The metadata of the cluster value 
  - `related`: The related cluster values of the cluster value (you can define a `type` for each relation type in the config which will not be mapped to a field of the API)
  - `uuid`: The UUID of the cluster value 
  - `value`: The value of the cluster value
  >Note: The fields `meta` can be formatted as the format of the data the API provides sometimes does not match the format defined by the [MISP galaxy format](https://www.misp-standard.org/rfc/misp-standard-galaxy-format.html#name-conventions-and-terminology). You can configure this using an extraction configuration.

### Extraction Configuration
The extraction configuration is a dictionary that maps the fields of the Tidal Cyber API to the fields of the MISP galaxy. It can be used to extract data stored in an object in the API response. The extraction configuration looks like this:
```json
{
  "extract": "<mode>",
  "key": "<key>",
  "subkey": "<subkey>"
}
```
**Extract modes**:

- `single`: Extracts a single value from the API response
- `multiple`: Extracts multiple values from the API response
- `reverse`: Gets the value of the key and writes it into an array (no subkey needed)

### "Private" Relations
The Tidal Cyber API provides relations between different objects. Some of these relations point to objects that are not part of the galaxies created based on the API response nor are they part of the MISP galaxy. These relations can be marked as `private` in the config file. For example:
```json
    "related": {
                "tactic": {
                    "mode": "public",
                    "dest-uuid": "tactic_id",
                    "type": "uses"
                },
                "sub_technique": {
                    "mode": "private",
                    "dest-uuid": "id",
                    "type": "sub-technique-of"
                }
            },
```

## Usage
```bash
python3 main.py create-galaxy -v <version> --type <galaxy_to_create>
```
To build all galaxies and clusters, run the following command:

```bash
python3 main.py create-galaxy -v <version> --all
```
