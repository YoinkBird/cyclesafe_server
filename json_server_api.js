"use strict";
/*
  src: https://stackoverflow.com/a/24468752
  for send, receive . is usuing async, doesn't mention it though
  src: https://stackoverflow.com/a/4033310
  another style, better varnames, explicit mention of async
 */
// URL for JSON host:
// origin URL, allows testing from arbitrary URL ('localhost', IP address, etc) : https://developer.mozilla.org/en-US/docs/Web/API/Window/location
var urlJsonServer = window.location.origin;
var jsonEndpoint = "rest/score";
var urlJsonServerRest = urlJsonServer + "/" + jsonEndpoint;
// vars relative to url
var jsonEndpointPost = jsonEndpoint + "/" + "upload";
var jsonEndpointGet  = jsonEndpoint + "/" + "retrieve";

/* send json */
function setVarAndLog(xhr){
  // callback(xhr.responseText);
  var jsonresp = JSON.parse(xhr.responseText);
  console.log('--- POST response received');
  console.log(JSON.stringify(jsonresp));
}
function httpPostAsync(myUrl, sendString, callback){
  var xhr_post = new XMLHttpRequest();
  xhr_post.open("POST",myUrl,true); // true : async
  xhr_post.setRequestHeader("Content-type", "application/json");
  // async - see the second source
  xhr_post.onreadystatechange = function (){
    if (xhr_post.readyState == 4 && xhr_post.status == 200){
      callback(xhr_post);
    }
  };
  xhr_post.send(sendString);
}

// demo usage
if(0){
  console.log('--- POST request sending');
  // TODO: verify response. this particular server returns the same json_str it received
  httpPostAsync(urlJsonServer, JSON.stringify({"lol":"hey"}), setVarAndLog);
  console.log('--- POST request sent');
}

/* receive json */
/* TODO: async this thingy, forgot how to callbacks though.
 * current method may already be using a callback to set the var.
 */

// async notes:
// assigned before request complete
// var muhjaysawns = JSON.stringify(xhr_get.responseText);
// printed out either before request complete, or then before assigned
// console.log(JSON.stringify(muhjaysawns));
var muhjaysawns;

function setJsonVarAndLog(xhr){
  muhjaysawns = JSON.parse(xhr.responseText);
  if(1){
    console.log('--- GET response received');
    console.log(JSON.stringify(muhjaysawns));
  }
}

function httpGetAsync(myUrl, callback){
  var xhr_get  = new XMLHttpRequest();
  xhr_get.open("GET",myUrl,true);
  xhr_get.setRequestHeader("Content-type", "application/json");
  // async
  xhr_get.onreadystatechange = function (){
    if (xhr_get.readyState == 4 && xhr_get.status == 200){
      callback(xhr_get);
    }
  };
  xhr_get.send(null);
}

// demo usage
if(0){
  console.log('--- GET request sending');
  // this url is a simple single-serving for now. no REST API
  httpGetAsync(urlJsonServer, setJsonVarAndLog);
  console.log('--- GET request sent');
}

// blocking
if(0){
  xhr.open("GET",urlJsonServer, false); // false for synchro
  console.log('--- blocking GET request sending');
  xhr.send(null);
  console.log('--- blocking GET request sent');
  var muhjaysawns = JSON.stringify(xhr.responseText);
  console.log(JSON.stringify(muhjaysawns));
}

/*-------------------------------------------------------------------------------- */ 
/* send json, receive response */
// alternative to promises... rabit hole!
// i.e. can't call httpGetAsync with callback on its own XMLHttpRequest
function httpPostSyncAndGetAsync(myUrl, sendString, callback){
  console.log('--- Log legend: [ ] unstarted | [_] current | [/] started | [x] complete ');
  var xhr_post = new XMLHttpRequest();
  // sync post
  xhr_post.open("POST",myUrl + "/" + jsonEndpointPost,false); // true : async, false: sync
  xhr_post.setRequestHeader("Content-type", "application/json");

  xhr_post.send(sendString);
  console.log(JSON.stringify(xhr_post.responseText));

  // async get
  console.log('--- GET request sending');
  httpGetAsync(myUrl + "/" + jsonEndpointGet, setJsonVarAndLog);
  console.log('--- GET request sent');
}

// demo usage
if(0){
  console.log('--- POST-and-GET request sending');
  // TODO: verify response. this particular server returns the same json_str it received
  // mock "response" from directions example
  var response = {"hey":"lol"};
  //httpPostAndGetAsync(urlJsonServer, JSON.stringify({"lol":"hey"}), setVarAndLog);
  httpPostSyncAndGetAsync(urlJsonServer, JSON.stringify(response), setVarAndLog);

  console.log('--- POST-and-GET request sent');
}
/*-------------------------------------------------------------------------------- */ 

/*-------------------------------------------------------------------------------- */ 
/* send json, receive response */
// alternative to promises... rabit hole!
// i.e. can't call httpGetAsync with callback on its own XMLHttpRequest
function httpPostSyncAndGetSync(myUrl, sendString, callback){
  console.log('--- Log legend: [ ] unstarted | [_] current | [/] started | [x] complete ');
  // sync post
  var xhr_post = new XMLHttpRequest();
  xhr_post.open("POST",myUrl + "/" + jsonEndpointPost,false); // true : async, false: sync
  xhr_post.setRequestHeader("Content-type", "application/json");

  xhr_post.send(sendString);
  console.log(JSON.stringify(xhr_post.responseText));

  // sync get
  var xhr_get = new XMLHttpRequest();
  xhr_get.open("get",myUrl + "/" + jsonEndpointGet ,false); // true : async, false: sync
  xhr_get.setRequestHeader("Content-type", "application/json");

  xhr_get.send(null);
  // TODO:  string is quoted twice, find out solution. JSON.parse will except called on an object, and it is not clear under which circumstances this responseText == response or why it has so many quotes
  var result = JSON.parse(JSON.parse(xhr_get.responseText));
  console.log(JSON.stringify(xhr_get.responseText));
  return result;
}

// demo usage
if(0){
  console.log('--- POST-and-GET request sending');
  // TODO: verify response. this particular server returns the same json_str it received
  // mock "response" from directions example
  var response = {"hey":"lol"};
  //httpPostAndGetAsync(urlJsonServer, JSON.stringify({"lol":"hey"}), setVarAndLog);
  httpPostSyncAndGetSync(urlJsonServer, JSON.stringify(response), setVarAndLog);

  console.log('--- POST-and-GET request sent');
}
/*-------------------------------------------------------------------------------- */ 

console.log('--- --- ---');
    //<!-- </json_server_api> -->
