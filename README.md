![MIT license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

# log-audits-to-elasticsearch
Designed for developers and system administrators, this Docker solution provides a centralized and searchable audit logging system
leveraging Elasticsearch's powerful scalability and search capabilities.

## Table of Contents
- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
    - [Installation](#installation)
      - [Clone the Repository](#clone-the-repository)
      - [Build and Run the Container](#build-and-run-the-container)
- [Usage](#usage)
  - [Configuration](#configuration)
    - [Environment File (.env) for Docker](#environment-file-env-for-docker)
    - [Configuration File (config.yaml) for FastAPI](#configuration-file-configyaml-for-fastapi)
  - [FastAPI endpoints](#fastapi-endpoints)
  - [Audit Logs](#audit-logs)
    - [Audit Log Schema (Elasticsearch)](#audit-log-schema-elasticsearch)
    - [Audit Log ES Document Example](#audit-log-es-document-example)
    - [Create a Single Audit Log](#create-a-single-audit-log)
    - [Create Bulk Audit Logs](#create-bulk-audit-logs)
    - [Create Automated Bulk Audit Logs](#create-automated-bulk-audit-logs)
  - [Search Audit Logs](#search-audit-logs)
    - [Search Features](#search-features)
    - [Crafting Search Requests](#crafting-search-requests)
- [Running Backups](#running-backups)
  - [Executing Backups](#executing-backups)
  - [Automating Backups](#automating-backups)
- [Elasticsearch and Kibana](#elasticsearch-and-kibana)
  - [Accessing Elasticsearch](#accessing-elasticsearch)
  - [Accessing Kibana](#accessing-kibana)
- [License](#license)

## Introduction
The `log-audits-to-elasticsearch` project offers a robust, Docker-based solution for centralized audit logging.
Leveraging Elasticsearch's powerful search capabilities, it's designed to assist developers and system administrators in efficiently storing, searching, and managing audit logs.
This ensures high scalability for growing application needs, offering an invaluable tool for monitoring and security compliance.

## Getting Started

### Prerequisites
Before you begin, ensure you have installed the following tools:
- [Docker](https://docs.docker.com/get-docker/) (version 25.0.3 or newer)
- [Docker Compose](https://docs.docker.com/compose/install/) Compose (version 2.26.1 or newer)

### Installation
#### Clone the Repository
Start by cloning the project repository to your local machine:
```bash
git clone git@github.com:bulletinmybeard/log-audits-to-elasticsearch.git
````

#### Build and Run the Container
Navigate to the project directory and start the Docker containers. This step builds the Docker images if they're not already built or rebuilds them if any changes were made.

```bash
cd log-audits-to-elasticsearch
docker-compose up --build
```

[↑ Back to top](#table-of-contents)

## Usage
### Configuration
The smooth operation of the **log-audits-to-elasticsearch** application depends on correctly configuring two essential files:
* The `.env` file for Docker environments
* The `config.yaml` for the FastAPI application itself

#### Environment File (.env) for Docker
The `.env` file contains essential environment variables, such as Elasticsearch configuration parameters,
application port settings, and other required variables for various environments.

Duplicate the provided [.env-sample](.env-sample) file to create the `.env` file.

#### Configuration File (config.yaml) for FastAPI
Just as the `.env` file is essential for Docker, the `config.yaml` file configures the operational parameters of the FastAPI application.

Create the `config.yaml` by copying from [config-sample.yaml](config-sample.yaml).
This file will enable you to customize the FastAPI application settings, ensuring it operates according to your specific requirements.

### FastAPI endpoints
| Request Method | Endpoint                   | Authentication | Body/Get Query parameters          | Description                                                                                                                                                                     |
|----------------|----------------------------|----------------|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `GET`          | `/health`                  | None           | None                               | Health check endpoint.                                                                                                                                                          |
| `POST`         | `/create`                  | X-API-KEY      | JSON audit log                     | Create a single audit log entry.                                                                                                                                                |
| `POST`         | `/create-bulk`             | X-API-KEY      | JSON audit logs                    | Create up to 500 audit log entries at once.                                                                                                                                     |
| `POST`         | `/create/create-bulk-auto` | X-API-KEY      | `{ "bulk_limit": 500 }` (Optional) | Generates up to 500 fictitious audit log entries using the Faker library.<br>**Note**: Only available in the `development` environment to prevent accidental use in production. |
| `POST`         | `/search`                  | X-API-KEY      | JSON search parameters             | Combine multiple different search parameters and filters to run a search against the Elasticsearch index                                                                        |

> **Note**: To use endpoints that require an `X-API-KEY`, define the key in the `config.yaml`.

### Audit Logs
The log-audits-to-elasticsearch application provides a robust RESTful API tailored for systematic event and activity logging.
This ensures that critical information is captured efficiently within Elasticsearch, facilitating easy retrieval and analysis.

#### Audit Log Schema (Elasticsearch)
| Field             | Optional/Mandatory | Default Value | Description                                                             |
|-------------------|--------------------|---------------|-------------------------------------------------------------------------|
| timestamp         | Optional           | None          | The date and time when the event occurred, in ISO 8601 format.          |
| event_name        | Mandatory          | -             | Name of the event.                                                      |
| actor.identifier  | Mandatory          | -             | Unique identifier of the actor. Can be an email address, username, etc. |
| actor.type        | Mandatory          | None          | Type of actor, e.g., 'user' or 'system'.                                |
| actor.ip_address  | Optional           | None          | IPv4 address of the actor (will be stored anonymized).                  |
| actor.user_agent  | Optional           | None          | User agent string of the actor's device.                                |
| application_name  | Mandatory          | -             | Application name.                                                       |
| module            | Mandatory          | -             | Module name.                                                            |
| action            | Mandatory          | -             | Action performed.                                                       |
| comment           | Optional           | None          | Optional comment about the event.                                       |
| context           | Optional           | None          | The operational context in which the event occurred.                    |
| resource.type     | Optional           | None          | Type of the resource that was acted upon.                               |
| resource.id       | Optional           | None          | Unique identifier of the resource.                                      |
| operation         | Optional           | None          | Type of operation performed.                                            |
| status            | Optional           | None          | Status of the event.                                                    |
| endpoint          | Optional           | None          | The API endpoint or URL accessed, if applicable.                        |
| server.hostname   | Optional           | None          | Hostname of the server where the event occurred.                        |
| server.vm_name    | Optional           | None          | Name of the virtual machine where the event occurred.                   |
| server.ip_address | Optional           | None          | IP address of the server  (will be stored anonymized).                  |
| meta              | Optional           | {}            | Optional metadata about the event.                                      |

#### Audit Log ES Document Example
```json
{
  "timestamp": "2024-04-06T23:02:25.934470+02:00",
  "event_name": "data_deletion",
  "actor": {
    "identifier": "buckleyjames",
    "type": "user",
    "ip_address": "192.0.0.0",
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.1 (KHTML, like Gecko) Chrome/54.0.855.0 Safari/536.1"
  },
  "application_name": "user-management-service",
  "module": "admin",
  "action": "DELETE",
  "comment": "Monthly housekeeping.",
  "context": "admin_user_management",
  "resource": {
    "type": "user_data"
  },
  "operation": "delete",
  "status": "success",
  "endpoint": "/user/{user_id}/delete",
  "server": {
    "hostname": "server-01",
    "vm_name": "vm-01",
    "ip_address": "10.10.0.0"
  },
  "meta": {
    "api-version": "1",
    "app-version": "1.0.0"
  }
}
```

#### Create a Single Audit Log
To record an individual log entry, dispatch a `POST` request to the endpoint `/create`. The request must include a JSON payload detailing the specifics of the log entry.

#### Create Bulk Audit Logs
To log up to `500` entries in a single operation, utilize the `/create-bulk` endpoint. Similar to the single entry endpoint, this requires a JSON payload containing an array of log entry details.

#### Create Automated Bulk Audit Logs
The `/create/create-bulk-auto` endpoint provides an automated solution for generating and logging up to `500` demo audit log entries simultaneously. Leveraging Python's Faker library, this endpoint is ideal for populating your Elasticsearch with realistic yet fictitious data for development or testing purposes.

> It's important to note that `/create/create-bulk-auto` is only available in the development environment to prevent accidental use in production.

These endpoints serve as your gateway to effective log management, enabling you to maintain a comprehensive audit trail of system events and user activities.

### Search Audit Logs
To search within the audit logs, send a POST request to the `/search` endpoint.
This endpoint accepts a JSON payload that defines your search criteria and filters,
allowing for complex queries such as range searches, text searches, and field-specific searches.

#### Search Features
* **Flexible Querying:** Tailor your searches by using a variety of query parameters to refine results according to specific requirements, such as time frames, user actions, and status codes.
* **Range Searches:** Specify start and end dates to retrieve logs from a specific period.
* **Text Searches:** Utilize keywords or phrases to search within log entries for precise information.
* **Field-Specific Searches:** Focus your search on specific fields within the log entries for more targeted results.

#### Crafting Search Requests
Explore [SEARCH_GUIDE.md](SEARCH_GUIDE.md) for a deep dive into search query examples and instructions.

[↑ Back to top](#table-of-contents)

## Running Backups
To ensure data persistence and safety, it's crucial to back up data volumes regularly.
This includes volumes like `sa_elasticsearch_data` and `sa_kibana_data`.
To facilitate this, we use a BusyBox Docker container to execute the [volume_backups.sh](backup/volume_backups.sh) script for performing the backups.
The backup data is stored in the [backup folder](backup) for safekeeping.

### Executing Backups
To initiate the backup process through a Docker container, run the following command:
```bash
docker-compose run backup
```

### Automating Backups
To automate the backup process, you can schedule the backup operation using crontab. This enables the Docker container to run at predefined times without manual intervention.

First, ensure that the backup script is executable:
```bash
# Grant execute permissions to the backup script
chmod +x volume_backups.sh
```

Next, open your crontab file in edit mode:
```bash
# Open crontab in edit mode
crontab -e
```

Add the following line to your crontab to schedule a daily backup at 2 AM.
Ensure to replace `/path/to/your/` with the actual path to your `docker-compose.yml` file:
```bash
# Schedule daily backups at 2 AM
0 2 * * * docker-compose -f /path/to/your/docker-compose.yml run backup
```
This setup ensures that your data volumes are backed up daily, minimizing the risk of data loss and maintaining the integrity of your system.

[↑ Back to top](#table-of-contents)

## Elasticsearch and Kibana
Elasticsearch is used for storing, searching, and analyzing audit log documents,
while Kibana's frontend offers visual analytics on the data stored in Elasticsearch.

### Accessing Elasticsearch
ES is best accessed via cURL:
```bash
# Example: Retrieve the cluster health status
curl -X GET "http://localhost:9200/_cluster/health?pretty"
```
Documentation: [elasticsearch/reference/current/getting-started.html](https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started.html)

### Accessing Kibana
Access the Kibana dashboard via [http://localhost:5601](http://localhost:5601).
Documentation: [kibana/current/introduction.html](https://www.elastic.co/guide/en/kibana/current/introduction.html)

## License
This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
