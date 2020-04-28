Example Mutations and Queries
-----------------------------

You can just import the predefined mutations from `django_graphene_jwt.schema.mutations` and queries `django_graphene_jwt.schema.query`

Register a new user
```
mutation SignUp {
  jwtSignUp(password: "123", username: "abc") {
    token
  }
}
```

Sign in
```
mutation SignIn {
  jwtSignIn(username: "abc", password: "123") {
    token
    refreshToken
  }
}
```

Verify a token
```
mutation Verify {
  jwtVerifyToken(token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjIiLCJleHAiOjE1ODc5MDk2MzYsIm9yaWdJYXQiOjE1ODc5MDkzMzYsInJlZnJlc2hfdG9rZW4iOiI1N2NkYjQ4ZDIwYzYxMzU5ZTIzOTMzY2IzNzFhNzE3M2Y3NDU5MGFjIn0.cS8gmDHWKDOYAB2e5iPusIMHWocwdmRAWB-euip-9FM") {
    payload
  }
}
```

Refresh a token (the old one is still valid if it isn't expired yet)
```
mutation Refresh {
  jwtRefreshToken(refreshToken: "e64103b0e0001df7817adfad111cf0302cd10684") {
    token
    payload
    refreshToken
  }
}
```

Revoke a single Token
```
mutation Revoke {
  jwtRevokeToken(refreshToken: "ee620aa6eec8ea2a945073291057ca106169531b") {
    revoked
  }
}
```

Revoke all user related tokens (Logout of all devices - user must be logged in)
```
mutation RevokeAll {
  jwtRevokeAllTokens {
    revokedTokens
  }
}
```

Example public Field
```
query Hello {
  hello
}
```

Example protected Field
```
query HelloProtected {
  helloProtected
}
```

Patches
-------
GraphQl is returning errors in an extra `error` Field, the patch provided in the `patches.py` adds this functionallity.
It will also add a Trace if the server is in debug mode. 