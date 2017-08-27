import axios from 'axios';

const URL = '';
const CLIENT_ID = '';

function createClient(method, token) {
    var config = {
        baseURL: (URL === null ? window.location.origin : URL) + '/api'
    };
    if (method && token) {
        config.headers['Authorization'] = method + ' ' + token;
    }
    return axios.create(config);
}

var client = createClient();

function login(username, password, onSuccess, onError) {
    client.post('/oauth/token', {
        username: username,
        password: password,
        client_id: CLIENT_ID,
        grant_type: 'password'
    }).then(function (response) {
        if (response.status === 200) {
            onSuccess();
        } else {
            onError();
        }
    }).catch(function (error) {
        onError();
    });
}

export {
    client,
    login
};