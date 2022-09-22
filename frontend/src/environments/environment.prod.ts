export const environment = {
  production: true,
  apiServerUrl: 'https://coffee-shop-backend.onrender.com/', // the running FLASK api server url
  auth0: {
    url: 'amrikhudair.eu', // the auth0 domain prefix
    audience: 'https://coffee-shop.test', // the audience set for the auth0 app
    clientId: '6foUBjR8Uys0PRrhAEVJ5BF6lltFsYBX', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application.
  }
};
