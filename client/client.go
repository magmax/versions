package main

import (
        "os"
        "flag"
        "fmt"
        "bytes"
        "io/ioutil"
        "net/http"
        "encoding/json"
)

var empty = "<NOT SET>"
var url = flag.String("url", empty, "Url to connect to")
var host = flag.String("host", empty, "Hostname")
var cluster = flag.String("cluster", empty, "Cluster the host belongs to")
var application = flag.String("application", empty, "Application")
var version = flag.String("version", empty, "Version number")
var uri = flag.String("uri", empty, "URI to access the resource")

func send(url *string, data map[string]string) {
  jsonStr, err := json.Marshal(data)
  req, err := http.NewRequest("POST", *url, bytes.NewBuffer(jsonStr))
  req.Header.Set("Content-Type", "application/json")

  client := &http.Client{}
  resp, err := client.Do(req)
  if err != nil {
    panic(err)
  }
  defer resp.Body.Close()

  fmt.Println("response Status:", resp.Status)
  fmt.Println("response Headers:", resp.Header)
  body, _ := ioutil.ReadAll(resp.Body)
  fmt.Println("response Body:", string(body))
}


func main() {
  flag.Parse()
  if (*host == empty) {
    hostname, _ := os.Hostname()
    host = &hostname // beware!
  }
  if (*uri == empty) {
    fmt.Println("URI is mandatory")
    os.Exit(1)
  }
  if (*url == empty) {
    fmt.Println("URL is mandatory")
    os.Exit(1)
  }
  if (*application == empty) {
    fmt.Println("Application is mandatory")
    os.Exit(1)
  }
  if (*version == empty) {
    fmt.Println("Version is mandatory")
    os.Exit(1)
  }

  fmt.Println(*host)
  var data map[string]string
  data = make(map[string]string)
  data["host"] = *host
  data["uri"] = *uri
  data["application"] = *application
  data["version"] = *version
  if (*cluster != empty) {
    data["cluster"] = *cluster
  }
  send(url, data)
}
