// services/web/modules/config.js
export const CONFIG = {
    githubOwner: 'sleep-bugy',
    githubRepo: 'FrameworkPatcher',
    workflows: {
        android13: 'android13.yml',
        android14: 'android14.yml',
        android15: 'android15.yml',
        android16: 'android16.yml'
    },
    // API endpoints
    apiBaseUrl: '/api',
    endpoints: {
        devices: '/devices',
        deviceSoftware: '/devices/{codename}/software'
    }
};
