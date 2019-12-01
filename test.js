var express = require('express');
var session = require('express-session');
var cookieParser = require('cookie-parser');
var app = express();
//var memCachedStore = require('connect-memcached')(session);

app.use(cookieParser());
app.use(session({
      secret  : '3gpp_search_engine',
      key     : 'test',
      proxy   : 'true',
      /*store   : new memCachedStore({
        hosts: ['127.0.0.1:11211'], //this should be where your Memcached server is running
        secret: 'memcached-secret-key' // Optionally use transparent encryption for memcache session data 
    })*/
}));

var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({
  host: 'localhost:9200',
  log: 'trace',
  apiVersion: '7.4', // use the same version of your Elasticsearch instance
});

const fs = require('fs');
const url = require('url');

app.set("view engine","jade");

app.use(express.static('public'));

let run_search = (text, filterDoc) => {
  // Let's search!
    if (filterDoc === "")
      search_doc = '*'
    else
      search_doc = filterDoc

    if (String(JSON.stringify(text)).split(" ").length > 1)
    {
      if (filterDoc === "")
      {
        console.log("filterDoc is null")
        return client.search({
        index: search_doc,
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
                "size": 20
              }
            }
          }
          }
        }).then(result => {return result})
      }
      else {
        return client.search({
        index: search_doc,
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
          }
          }
        }).then(result => {return result})
      }
    }
    else
    {
      if (filterDoc === "")
      {
        return client.search({
        index: search_doc,
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
      else {
        return client.search({
        index: search_doc,
        stats:"_index",
        size:200,
        body: {
          "query": {
            "multi_match": {
              "query": JSON.stringify(text),
              "fields": ["key^5", "desc"]
              }
          }
        }
        }).then(result => {return result})
      }
    }
}

var bodyParser =require("body-parser");
app.use(bodyParser.urlencoded({ extended: false }));

app.get('/', function (req, res) {
    var sessionData = req.session;
    console.log(sessionData.id)
    //sessionData.uuid = String(uuid)
    res.sendFile('/home/ubuntu/3gpp_search_engine/3gpp_search_engine_web/index.html');
    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    console.log(ip)
});

app.get('/sort', function (req, res) {
    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    search_group_key = ip + "-" + 'group'

    request_url = decodeURIComponent(req.url)
    console.log(request_url)
    var filterDoc = request_url.split('?')[1].split(' ')[0];
    var key = request_url.split('search_text=')[1]
    console.log(search_text)
    console.log(filterDoc)
    groups = JSON.parse(req.session.groups)
    run_search(search_text, filterDoc).then(function(results)
    {
  	search_results = results.hits.hits
        console.log(groups)

  	res.render('search_results', {searchResultList : search_results, searchKey : key, searchGroups : groups} );
	req.session.groups = JSON.stringify(groups)
    }
    ).catch(console.log)
});

app.get('/submit-search-data', function (req, res) {
    var key = req.query.search_text;
    var ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    search_group_key = ip + "-" + 'group'
    console.log(search_group_key)
    console.log(req.session.id)
    request_url = req.url
    search_text = request_url.split('search_text=')[1].replace(/\+/g, ' ')
    console.log(search_text)
    run_search(search_text, "").then(function(results)
    {
	search_results = results.hits.hits
	groups = results.aggregations.group_by_index
        console.log(groups)

	res.render('search_results', {searchResultList : search_results, searchKey : key, searchGroups : groups} );
	req.session.groups = JSON.stringify(groups)
        req.session.save(function(err){})
    }).catch(console.log)

});

app.get('/details', function (req, res)
{
    request_url = decodeURIComponent(req.url)
    info = request_url.split('?')[1]
    index = info.split(' ')[0]
    numbering = info.split('numbering=')[1].split(' ')[0]
    search_text = info.split('search_text=')[1]
    len = numbering.split(".").length
    values = numbering.split(".")
    if (len > 3)
    {
	numbering = values[0] + '.' + values[1] + '.' + values[2]
    }

    var series = String(index).substr(0, 2)
    var ver = String(index).split("-")[1]
    var spec = String(index).split("-")[0]
    console.log(spec)
    spec = spec.substr(0, 2) + "." + spec.substr(-3)
    html_file = "/spec/" + series + "/" + spec + "/" + ver + "/slice_html/CLA_" + numbering + ".html" + "?hightlight=" + search_text;

    console.log(html_file)
    res.redirect(html_file)
}
)

var server = app.listen(5000, function () {
    console.log('Node server is running..');
});
