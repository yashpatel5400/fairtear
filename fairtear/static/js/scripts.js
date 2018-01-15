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
    analysisInProgress: false,
    analysisError: false,
    analysisOutput: '',
};

function reducer(state, action) {
    var newState = Object.assign({}, state);
    switch (action.type) {
        case 'LOADED_XCSV':
            newState.attributes = action.data[0];
            newState.dataCount = action.data.length;
            break;
        case 'SET_QUALIFIED':
            newState.qualifiedEnabled = action.enabled;
            break;
        case 'ANALYSIS_START':
            newState.analysisInProgress = true;
            newState.analysisError = false;
            newState.analysisOutput = '';
            break;
        case 'ANALYSIS_OUTPUT':
            newState.analysisOutput += action.data;
            break;
        case 'ANALYSIS_COMPLETE':
            newState.analysisInProgress = false;
            newState.analysisError = false;
            break;
        case 'ANALYSIS_ERROR':
            newState.analysisInProgress = false;
            newState.analysisError = true;
            break;
        default:
            console.error('Unrecognized action type: ' + action.type);
            break;
    }
    return newState;
}

var store = Redux.createStore(reducer, initialState);

var currentState = {};
var attributesPresent = state => state.attributes && state.attributes.length > 0;
var visibilityMap = {
    'js-model-attributes-help': state => !attributesPresent(state),
    'js-model-attributes-select': state => attributesPresent(state),
    'js-qualified-select': state => state.qualifiedEnabled,
    'js-xcsv-validation': state => state.dataCount !== null,
    'js-analysis-in-progress': state => state.analysisInProgress,
    'js-analysis-error': state => state.analysisError,
    'js-analysis-output-wrap': state => state.analysisOutput,
};

function render(nextState) {
    console.log(currentState, nextState);

    // Show/hide elements
    for (var className of Object.keys(visibilityMap)) {
        if (visibilityMap[className](nextState)) {
            $(`.${className}`).show();
        } else {
            $(`.${className}`).hide();
        }
    }

    // Update select elements
    if (nextState.attributes && nextState.attributes.length > 0 && nextState.attributes !== currentState.attributes) {
        var defaultItem = $('<option selected disabled>Choose attribute...</option>');
        var attributeItems = nextState.attributes.map(a => $(`<option value="${a}">${a}</option>`));
        $('.js-attribute-input').empty().append(defaultItem).append(attributeItems);
    }

    // Update csv validation
    $('.js-xcsv-validation').text(`Loaded ${nextState.dataCount} data points.`);

    // Update submit button
    $('.js-analysis-submit').attr('disabled', nextState.analysisInProgress);

    // Update analysis output
    $('.js-analysis-output')
        .text(nextState.analysisOutput)
        .scrollTop($('.js-analysis-output')[0].scrollHeight);

    currentState = nextState;
}

store.subscribe(() => render(store.getState()));
render(initialState);

$(function () {
    $('.custom-file-input').change(function (e) {
        if (this.files.length == 0) return;
        var file = this.files[0];
        $(this).next().text(file.name);
    });

    $('#data').submit(function (e) {
        e.preventDefault();
        store.dispatch({ type: 'ANALYSIS_START' });
        var form_data = new FormData(this);
        var seen = 0;
        var buffer = "";
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/_analyze_data',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                if (data.errors) {
                    // TODO: handle validation errors
                    store.dispatch({ data, type: 'ANALYSIS_ERROR' });
                } else {
                    store.dispatch({ data, type: 'ANALYSIS_COMPLETE' });
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                store.dispatch({ type: 'ANALYSIS_ERROR' });
            },
            xhrFields: {
                onprogress: function (e) {
                    var response = e.currentTarget.response.substring(seen);
                    seen += response.length;
                    buffer += response;
                    var newline = buffer.indexOf('\n');
                    while (newline !== -1) {
                        store.dispatch({ type: 'ANALYSIS_OUTPUT', data: buffer.substring(0, newline+1) });
                        buffer = buffer.substring(newline+1);
                        newline = buffer.indexOf('\n');
                    }
                }
            },
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
