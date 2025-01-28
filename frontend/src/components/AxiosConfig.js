// src/axiosConfig.js
import axios from 'axios';
import { getCSRFToken } from './csrf';

axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
const csrfToken = getCSRFToken();
console.log("CSRF Token:", csrfToken);
axios.defaults.headers.common['X-CSRFToken'] = getCSRFToken();

export default axios;
