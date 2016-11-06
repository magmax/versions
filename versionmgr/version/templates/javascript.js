function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

var Content = function(){
  var _anchor = null;

  var clear = function(){
    _anchor.html('');
  };

  var show = function(anchor, content) {
    console.log(content);
    if (content === null) {
      return;
    }
    if ($.isPlainObject(content)) {
      var title = $('<a>', {href: '#', text: content['label'] ? content['label'] : content['name']});
      var card = $('<div>', {'class': 'card'});
      var cardTitle = $('<div>', {'class': 'card-header'});
      var cardBody = $('<div>', {'class': 'card-block'});
      title.click({url: content['url']}, load);
      card.append(cardTitle);
      card.append(cardBody);
      cardTitle.append(title);
      anchor.append(card);

      for (var i in content) {
        if ($.inArray(i, ['id', 'label', 'name', 'url']) != -1) {
          continue;
        }
        if ( content[i] == '' || content[i] == null || content[i] == [] || content[i] == {}) {
          continue;
        }

        var div = $('<div>', {'class': 'row'});
        var div1 = $('<div>', {'class': 'col-md-2', text: i});
        var div2 = $('<div>', {'class': 'col-md-10'});
        div.append(div1);
        div.append(div2);
        cardBody.append(div);
        show(div2, content[i]);
      }
    } else if ($.isArray(content)) {
      var ul = $('<ul>', {'class': 'list-group', 'style': 'list-style-type: none'});
      anchor.append(ul);
      for (var i in content) {
        var li = $('<li>');
        ul.append(li);
        show(li, content[i]);
      }
    } else {
      anchor.html($('<span>', {text: content}));
    }
  };

  var load = function(event) {
    var url = event.data.url;
    clear();
    history.pushState(null, null, '#' + url);
    $.get(url, function(response){
      show(_anchor, response.results ? response.results : response);
    });
  };

  var init = function(anchor){
    _anchor = anchor;
  };

  return {
    init: init,
    load: load,
  }
}


var NavigationBar = function(){
  var _content = null;
  var _anchor = null;

  var setMenu = function(links) {
    for (var name in links) {
      var link = $('<a>', {
        href: '#',
        'class': 'nav-link',
        text: capitalize(name),
      });
      link.click({url: links[name]}, _content.load);
      var item = $('<li>', {'class': 'nav-item'});

      item.append(link);
      _anchor.append(item);
    }
  }

  var init = function(anchor, content) {
    _content = content;
    _anchor = anchor;

    $.get({% url 'api-root' %}, function(response){
      setMenu(response);
    })

  };

  return {
    init: init
  };
};

$(document).ready(function(){
  var content = Content();
  var navigation = NavigationBar();

  content.init($('#content'));
  navigation.init($('#menu'), content);
});
