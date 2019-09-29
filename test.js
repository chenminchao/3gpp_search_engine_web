var express = require('express');
var app = express();

const { Client } = require('@elastic/elasticsearch')
const client = new Client({ node: 'http://localhost:9200' })

app.set("view engine","jade");

let run_search = text => {
  // Let's search!
  return client.search({
    index: '*',
    // type: '_doc', // uncomment this line if you are using Elasticsearch ≤ 6
    body: {
      query: {
        match: { desc: JSON.stringify(text) }
      }
    }
  }).then(result => {return result})

}

var bodyParser =require("body-parser");
app.use(bodyParser.urlencoded({ extended: false }));

app.get('/', function (req, res) {
    res.sendFile('C:\\3gpp_search_engine\\3gpp_search_engine_web\\index.html');
});

app.get('/submit-search-data', function (req, res) {
	var key = req.query.search_text;
	run_search(key).then(function(results)
		{
			search_results = results.body.hits.hits
			console.log(search_results)
			res.render('search_results', {searchResultList : search_results} );
			req.app.locals.search_results = JSON.stringify(search_results)
		}
	).catch(console.log)

});

app.get('/details', function (req, res)
	{
		id = req.url.split("?")[1];
		saved_results = JSON.parse(req.app.locals.search_results)
		res.render('description', {search_desc : saved_results[id]})
	}
)

var server = app.listen(5000, function () {
    console.log('Node server is running..');
});
