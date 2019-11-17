var express = require('express');
var app = express();

const { Client } = require('@elastic/elasticsearch')
const client = new Client({ node: 'http://localhost:9200' })

const fs = require('fs');

app.set("view engine","jade");

app.use(express.static('public'));

var LocalStorage = require('node-localstorage').LocalStorage,
localStorage = new LocalStorage('./scratch');

let run_search = text => {
  // Let's search!
    if (String(JSON.stringify(text)).split(" ").length > 1)
    {
        return client.search({
        index: '*',
        stats:"_index",
        size:200,
        body: {
          "query":{
              "bool": {
              "should": [
                {
                  "match_phrase": {
                    "key": {
                      "query": JSON.stringify(text),
                      "slop": 1
                    }
                  }
                },
                {
                  "match_phrase": {
                    "desc": {
                      "query": JSON.stringify(text),
                      "slop": 1
                    }
                  }
                }
              ]
            }
          },
          "aggs": {
            "group_by_index": {
              "terms": {
                "field": "_index",
                "size": 10
              }
            }
          }
          }
        }).then(result => {return result})
    }
    else
    {
        return client.search({
        index: '*',
        stats:"_index",
        size:200,
        body: {
          "query": {
            "multi_match": {
              "query": JSON.stringify(text),
              "fields": ["key^5", "desc"]
              }
          },
          "aggs": {
            "group_by_index": {
              "terms": {
                "field": "_index",
                "size": 10
              }
            }
          }
        }
        }).then(result => {return result})
    }
}

var bodyParser =require("body-parser");
app.use(bodyParser.urlencoded({ extended: false }));

app.get('/', function (req, res) {
    res.sendFile('C:\\3gpp_search_engine\\3gpp_search_engine_web\\index.html');
    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    console.log(ip)
});

app.get('/sort', function (req, res) {
    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    search_results_key = ip + "-" + 'search_results'
    search_group_key = ip + "-" + 'group'
    search_key_key = ip + "-" + 'key'
    operation_key = ip + "-" + 'operation'
    filtered_search_results_key = ip + "-" + 'filtered_search_results'

    var filterDoc = req.originalUrl.split('?')[1];
    searchResults = JSON.parse(localStorage.getItem(search_results_key))
    groups = JSON.parse(localStorage.getItem(search_group_key))
    key = localStorage.getItem(search_key_key)

    var filterSearchResults = [];
    for(var item in searchResults)
    {
        if(String(filterDoc) == (String(searchResults[item]._index)))
        {
            console.log(String(filterDoc));
            console.log(String(searchResults[item]._index));
            filterSearchResults.push(searchResults[item]);
        }
    }
    localStorage.setItem(filtered_search_results_key, JSON.stringify(filterSearchResults))
    localStorage.setItem(operation_key, "sort")
    res.render('search_results', {searchResultList : filterSearchResults, searchKey : key, searchGroups : groups} );
});

app.get('/submit-search-data', function (req, res) {
	var key = req.query.search_text;
  var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
  search_results_key = ip + "-" + 'search_results'
  search_group_key = ip + "-" + 'group'
  search_key_key = ip + "-" + 'key'
  operation_key = ip + "-" + 'operation'
  console.log(search_group_key)
	run_search(key).then(function(results)
		{
			search_results = results.body.hits.hits
			groups = results.body.aggregations.group_by_index
      console.log(groups)

			res.render('search_results', {searchResultList : search_results, searchKey : key, searchGroups : groups} );
      localStorage.setItem(search_results_key, JSON.stringify(search_results))
      localStorage.setItem(search_group_key, JSON.stringify(groups))
      localStorage.setItem(search_key_key, key)
      localStorage.setItem(operation_key, "search")
		}
	).catch(console.log)

});

app.get('/details', function (req, res)
	{
    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    search_results_key = ip + "-" + 'search_results'
    search_group_key = ip + "-" + 'group'
    search_key_key = ip + "-" + 'key'
    operation_key = ip + "-" + 'operation'
    filtered_search_results_key = ip + "-" + 'filtered_search_results'

		id = req.url.split("?")[1];
    if(localStorage.getItem(operation_key) == "search")
    {
        saved_results = JSON.parse(localStorage.getItem(search_results_key))
    }
    else
    {
        saved_results = JSON.parse(localStorage.getItem(filtered_search_results_key))
    }
		numbering = String(saved_results[id]._source.numbering);
    index = String(saved_results[id]._index);
    console.log(index)
		len = String(saved_results[id]._source.numbering).split(".").length
		values = String(saved_results[id]._source.numbering).split(".")
		if (len > 3)
		{
			numbering = values[0] + '.' + values[1] + '.' + values[2]
		}

    var ver = String(index).split("-")[1]
    var spec = String(index).split("-")[0]
    console.log(spec)
    spec = spec.substr(0, 2) + "." + spec.substr(-3)
    search_text = localStorage.getItem(search_key_key);
    html_file = "/spec/" + ver + "/" + spec + "/slice_html/" + numbering + ".html" + "?hightlight=" + search_text;

    console.log(html_file)
    res.redirect(html_file)
	}
)

var server = app.listen(5000, function () {
    console.log('Node server is running..');
});
