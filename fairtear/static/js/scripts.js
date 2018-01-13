var sensitiveCounter = 0;
var qualifiedCounter = 0;
var fairnessCounter  = 0;

function addInput(divName){
    var newdiv = document.createElement('div');
    var counter;
    if      (divName == "sensitive") { sensitiveCounter++; counter = sensitiveCounter; }
    else if (divName == "qualified") { qualifiedCounter++; counter = qualifiedCounter; }
    else if (divName == "fairness")  { fairnessCounter++;  counter = fairnessCounter;  }

    newdiv.innerHTML = `
    <input class="col-sm-3" type="text" placeholder="attribute" 
        name="${ divName }_attribute_${ counter }">
    <select class="col-sm-3" name="${ divName }_conditional_${ counter }">
      <option value=">">></option>
      <option value="=">=</option>
      <option value="<"><</option>
    </select> 
    <input class="col-sm-3" type="text" placeholder="threshold" 
        name="${ divName }_threshold_${ counter }">`;

    document.getElementById(divName).appendChild(newdiv);
}

var initialState = {
    attributes: null,
    qualifiedEnabled: false,
    dataCount: null,
    labelsCount: null,
};

function reducer(state, action) {
    var newState = Object.assign({}, state);
    switch (action.type) {
        case 'LOADED_XCSV':
            newState.attributes = action.data[0];
            newState.dataCount = action.data.length;
            break;
        case 'LOADED_YCSV':
            newState.labelsCount = action.data.length;
            break;
        case 'SET_QUALIFIED':
            newState.qualifiedEnabled = action.enabled;
            break;
        default:
            console.error('Unrecognized action type: ' + action.type);
            break;
    }
    return newState;
}

var store = Redux.createStore(reducer, initialState);

store.subscribe(() => {
    console.log(store.getState());
    
});

$(function() {
  $('a#analyze').bind('click', function() {
    var form_data = new FormData($('#data')[0]);
    $.ajax({
        type: 'POST',
        url: $SCRIPT_ROOT + '/_analyze_data',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            $("#result").text(data.result);
        }
    });
    return false;
  });

  $('#xcsv').change(function (e) {
    if (this.files.length == 0) return;
    var file = this.files[0];
    Papa.parse(file, {
        complete: function ({ data }) {
            store.dispatch({ data, type: 'LOADED_XCSV' });
        },
    });
  });

  $('.js-enable-qualified').change(function (e) {
    store.dispatch({ type: 'SET_QUALIFIED', enabled: this.checked });
  });
});
