import axios from 'axios';
import config from './config';

function createClient(method, token) {
    let options = {
        baseURL: (config.URL === null ? window.location.origin : config.URL) + '/api',
        headers: {}
    };
    if (method && token) {
        options.headers['Authorization'] = method + ' ' + token;
    }
    return axios.create(options);
}

let client = createClient(config.TOKEN_TYPE, config.TOKEN_VALUE);

function login(username, password, onSuccess, onError) {
    client.post('/oauth/token', {
        username: username,
        password: password,
        client_id: config.CLIENT_ID,
        grant_type: 'password'
    }).then(response => {
        if (response.status === 200) {
            onSuccess();
        } else {
            onError();
        }
    }).catch(() => {
        onError();
    });
}

export {
    client,
    login
};