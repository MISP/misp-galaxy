## How to contribute?

In the world of threat intelligence, there are many different models or approaches to order, classify or describe threat actors, threats or activity groups. We welcome new ways of describing threat intelligence 
as the galaxy model allows to reuse the ones you use or trust for your organization or community.

Fork the project, update or create elements or clusters and make a pull-request.

We recommend to validate the JSON file using [jq](https://stedolan.github.io/jq/) and [validate_all.sh](https://github.com/MISP/misp-galaxy/blob/master/validate_all.sh) before doing a pull-request.

### Dependencies for testing your contributions

To create your own Galaxies the following tools are needed to run the validation scripts.

- jsonschema (>v2.4)
- jq
- moreutils (sponge)

On a Debian flavoured distribution you can potentially do this:

```bash
sudo apt install jq moreutils python3-jsonschema
sudo wget -O /usr/local/bin/jsonschema https://gist.githubusercontent.com/SteveClement/e6ac60e153e9657913000216fc77c6ef/raw/c273ace06ad338d609dd2c84a0a6e215a268ea11/jsonschema
sudo chmod +x /usr/local/bin/jsonschema # This will only work with jsonschema >2.4 (before no CLI interface was available)
```


