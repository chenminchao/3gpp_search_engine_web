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
		//res.sendFile('C:\\3gpp_search_engine\\3gpp_search_engine_web\\load_test_2.html');
});

app.get('/submit-search-data', function (req, res) {
	var key = req.query.search_text;
	run_search(key).then(function(results)
		{
			search_results = results.body.hits.hits
			//console.log(search_results)
			res.render('search_results', {searchResultList : search_results} );
			req.app.locals.search_results = JSON.stringify(search_results)
		}
	).catch(console.log)

});

app.get('/details', function (req, res)
	{
		id = req.url.split("?")[1];
		saved_results = JSON.parse(req.app.locals.search_results)
		numbering = String(saved_results[id]._source.numbering);
		len = String(saved_results[id]._source.numbering).split(".").length
		values = String(saved_results[id]._source.numbering).split(".")
		if (len > 3)
		{
			numbering = values[0] + '.' + values[1] + '.' + values[2]
		}

    html_file = "/" + numbering + ".html"
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
