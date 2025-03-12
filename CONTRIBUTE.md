## How to contribute?

In the world of threat intelligence, various models and approaches exist to categorize, classify, or describe threat actors, threats, or activity groups. We welcome new methodologies for describing threat intelligence, as the galaxy model allows you to integrate the ones you rely on or trust for your organization or community.

Feel free to fork the project, update or create new elements or clusters, and submit a pull request.

We recommend to validate the JSON file using [jq](https://stedolan.github.io/jq/) and [validate_all.sh](https://github.com/MISP/misp-galaxy/blob/master/validate_all.sh) before doing a pull-request.

### Recommendations per Galaxy Cluster

If you want to contribute to an existing galaxy cluster, we advise you to review some of the guidelines:

- If the galaxy is automatically generated from an original source (e.g., MITRE ATT&CK or similar), we recommend using the associated tools available in [./tools](https://github.com/MISP/misp-galaxy/tree/main/tools) to update and generate the galaxy.
- If the galaxy is manually maintained in this repository, such as the [threat-actor](https://github.com/MISP/misp-galaxy/blob/main/clusters/threat-actor.json) cluster, you can directly update the JSON cluster, use [jq_all_the_things](https://github.com/MISP/misp-galaxy/blob/main/jq_all_the_things.sh), and make a pull request (PR).

#### Meta and Recommendations for Specific Clusters

##### `threat-actor` MISP Galaxy

- `refs` is an array of referenced URLs. We strongly recommend using the original source for the reference cluster. If you have additional URLs (not the original reference to the threat-actor name), we recommend using `additional_refs`.
- Every meta field starting with `cfr-` must be related to information found on cfr.org.
- `attribution-confidence` is the confidence level for the threat actor's country of origin. The value ranges between `0` and `100`. By default, it's set to `50`.


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


