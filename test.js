var express = require('express');
var app = express();

const { Client } = require('@elastic/elasticsearch')
const client = new Client({ node: 'http://localhost:9200' })

app.set("view engine","jade");

app.use(express.static('public'));

//const jsdom = require("jsdom");
//const { JSDOM } = jsdom;

let run_search = text => {
  // Let's search!
  a = 1
  if (a == 1)
  {
    return client.search({
    index: '*',
    stats:"_index",
    size:200,
    body: {
      "query": {
        "match_phrase": {
          "key": JSON.stringify(text)
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
        // type: '_doc', // uncomment this line if you are using Elasticsearch ≤ 6
        stats:"_index",
        size:200,
        body: {
          "query": {
            "bool": {
              "should": [
                {
                  "multi_match": {
                    "query": JSON.stringify(text),
                    "fields": ["key", "desc"]
                  }
                },
                {
                  "prefix": {
                    "key": {
                      "value": JSON.stringify(text)
                    }
                  }
                },
                {
                  "prefix": {
                    "desc": {
                      "value": JSON.stringify(text)
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

    /*      query: {
            match: { desc: JSON.stringify(text) }
          }*/
        }
      }).then(result => {return result})
  }

}

var bodyParser =require("body-parser");
app.use(bodyParser.urlencoded({ extended: false }));

app.get('/', function (req, res) {
		res.sendFile('C:\\hackathon\\3gpp_search_engine_web\\index.html');
		//res.sendFile('C:\\3gpp_search_engine\\3gpp_search_engine_web\\test_mark.html');
});

app.get('/sort', function (req, res) {	
    var filterDoc = req.originalUrl.split('?')[1];
    searchResults =  JSON.parse(req.app.locals.search_results)
    groups = req.app.locals.groups;
	key = req.app.locals.searchKey;
	
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
    console.log(filterSearchResults);
    req.app.locals.search_results = JSON.stringify(filterSearchResults);
    res.render('search_results', {searchResultList : filterSearchResults, searchKey : key, searchGroups : groups} );
});

app.get('/submit-search-data', function (req, res) {
	var key = req.query.search_text;
	run_search(key).then(function(results)
		{
			search_results = results.body.hits.hits
			groups = results.body.aggregations.group_by_index

			res.render('search_results', {searchResultList : search_results, searchKey : key, searchGroups : groups} );
			req.app.locals.search_results = JSON.stringify(search_results)
			req.app.locals.groups = groups
			req.app.locals.searchKey = key
		}
	).catch(console.log)

});

app.get('/details', function (req, res)
	{
		id = req.url.split("?")[1];
		saved_results = JSON.parse(req.app.locals.search_results)
		numbering = String(saved_results[id]._source.numbering);
    index = String(saved_results[id]._index);
    console.log(index)
		len = String(saved_results[id]._source.numbering).split(".").length
		values = String(saved_results[id]._source.numbering).split(".")
		if (len > 3)
		{
			numbering = values[0] + '.' + values[1] + '.' + values[2]
		}

    html_file = "/" + index + "/" + numbering + ".html"
    console.log(html_file)
    res.redirect(html_file)
		//link_html_file = "C:\\3gpp_search_engine\\3gpp_search_engine_web\\parsed_htmls\\" + numbering + ".html"
		//console.log(link_html_file)
		//res.sendFile(link_html_file)
		//res.render('description', {search_desc : saved_results[id]})
		/*JSDOM.fromFile("C:\\3gpp_search_engine\\3gpp_search_engine_web\\23401-g30.htm").then(dom => {
  		const window = dom.window;
			window.document.getElementById("test").href = "#_Toc11133729";
			console.log(window.document.getElementById("test").innerHTML);
			res.send(dom.serialize());
		});*/
	}
)

var server = app.listen(5000, function () {
    console.log('Node server is running..');
});
