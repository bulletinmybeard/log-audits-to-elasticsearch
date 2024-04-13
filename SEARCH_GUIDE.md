# Search Guide
If you don't have enough audit logs available, run the bash script [create_random_log_entries.sh](create_random_log_entries.sh) to generate as many as you need.

## Table of Contents
- [Quick Start](#quick-start)
- [Understanding Search Queries](#understanding-search-queries)
- [Crafting Basic Search Requests](#crafting-basic-search-requests)
- [Advanced Search Techniques](#advanced-search-techniques)
    - [Boolean Operations](#boolean-operations)
    - [Range Searches](#range-searches)
    - [Wildcard Searches](#wildcard-searches)
    - [Fuzzy Searches](#fuzzy-searches)
- [Using Aggregations](#using-aggregations)
- [Tips for Optimizing Your Searches](#tips-for-optimizing-your-searches)
- [Common Search Scenarios](#common-search-scenarios)

## Quick Start
### Search
```json
{
  "max_results": 25,
  "fields": ["timestamp", "actor.identifier", "event_name", "status", "actor.user_agent"],
}
```

### Result
```json
{
  "hits": 25,
  "docs": [
    {
      "actor": {
        "identifier": "s.jones",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/532.0 (KHTML, like Gecko) FxiOS/18.7c2467.0 Mobile/22A427 Safari/532.0"
      },
      "event_name": "role_update",
      "timestamp": "2024-01-01T00:18:02.089306",
      "status": "failure"
    },
    {
      "actor": {
        "identifier": "j.dot",
        "user_agent": "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.0; Trident/3.0)"
      },
      "event_name": "user_login",
      "timestamp": "2024-01-01T00:45:56.562149",
      "status": "success"
    },
    {
      "actor": {
        "identifier": "s.jones",
        "user_agent": "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 6.2; Trident/5.1)"
      },
      "event_name": "file_access",
      "timestamp": "2024-01-01T00:59:16.445467",
      "status": "failure"
    },
    ...
  ],
  "aggs": []
}

```
## Understanding Search Queries
## Crafting Basic Search Requests
## Advanced Search Techniques
### Boolean Operations
### Range Searches
#### Search
```bash
{
  "fields": ["timestamp", "event_name", "status"],
  "filters": [
    {
      "field": "timestamp",
      "type": "range",
      "value": "today"
    }
  ]
}

# OR

{
  "fields": ["timestamp", "event_name", "status"],
  "filters": [
    {
      "field": "timestamp",
      "type": "range",
      "gte": "2024-04-13T00:00:00",
      "lte": "2024-04-13T23:59:59"
    }
  ]
}
```
#### Result
```json
{
  "hits": 89,
  "docs": [
    {
      "event_name": "user_logout",
      "timestamp": "2024-04-13T00:09:48.288823",
      "status": "success"
    },
    {
      "event_name": "file_access",
      "timestamp": "2024-04-13T00:16:33.717124",
      "status": "failure"
    },
    {
      "event_name": "user_logout",
      "timestamp": "2024-04-13T00:21:00.517064",
      "status": "success"
    },
    ...
  ],
  "aggs": []
}
```
### Wildcard Searches
### Fuzzy Searches
## Using Aggregations
## Tips for Optimizing Your Searches
## Common Search Scenarios
### 
