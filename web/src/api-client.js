import axios from 'axios';

const URL = null;

export default axios.create({
    baseURL: (URL === null ? window.location.origin : URL) + '/api',
    headers: {'Authorization': 'Basic '}
});