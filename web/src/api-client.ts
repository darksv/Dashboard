import axios, {AxiosInstance} from 'axios';
import config from './config.ts';

function createClient(method: string, token: string): AxiosInstance {
    let options = {
        baseURL: (config.URL === null ? window.location.origin : config.URL) + '/api',
        headers: method && token
            ? {'Authorization': method + ' ' + token}
            : {}
    };
    return axios.create(options);
}

let client = createClient(config.TOKEN_TYPE, config.TOKEN_VALUE);

function login(username: string, password: string, onSuccess: () => void, onError: () => void) {
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