# fnval
A missing function level access control checker.

**This repo is in a quite early stage, so use with caution!**

## What is it trying to solve
> Applications do not always protect application functions properly. Sometimes, function level protection is managed
via configuration, and the system is misconfigured. Sometimes, developers must include the proper code checks, and
they forget.
>
> -- <cite>[OWASP’s Top 10](https://www.owasp.org/index.php/Top_10_2013-A7-Missing_Function_Level_Access_Control)</cite>

A determined malicious person can patiently study a web application to discover exposed endpoints, understand how
they are used and feed data to them to identify missing controls on the server-side. Sadly, not everyone stops there.

Automated vulnerability scanners usually do very poorly in these checks because they require extensive manually defined
configurations and expected outcome for every possible test-case.

## How it works
It accepts as input a concise configuration file in yaml with an application's users, urls and authentication settings.
It acts on behalf of every user listed in the configuration and attempts to access every url with all defined http
methods, and prints the actual and expected result.

## Example
Assuming there is an app called "Playlists" and allows users to manage and share their music playlists with other users.
To create a playlist or view someone else's playlist, a user must be authenticated. But, only the person who created a
playlist can edit or delete it.

Based on the requirements above we can design the following endpoints:

    1. Anonymous users can request:
        * GET / to view the homepage
        * GET /login to view the login page
    
    2. Authenticated users can request:
        * GET /playlist to view a playlist
        * POST /playlist to create a playlist
    
    3. Authorized users can request:
        * PUT /playlist/{playlist_id} to edit a playlist if it belongs to them
        * DELETE /playlist/{playlist_id} to delete a playlist if it belongs to them

The "{name}" placeholder in group #3 is automatically replaced with the right value for every user, based on their vars
dictionary. Any number of placeholders can be used in a url path as long as they are unique. When enumerating users, a
url is considered "unlocked" and thus added to the queue, if a user's vars include all keys defined in it.

Suppose we define two users: John and Paul. John created playlist called 'johns-favorites' with id = 1. The
configuration can look like this:

```yaml
---
app: Playlists

settings:
  auth: session
  root: http://localhost:8000
  login: /accounts/login
  username_field: username
  password_field: password
  csrf_cookie: csrftoken
  csrf_form: csrfmiddlewaretoken
  csrf_header: X-CSRFToken

users:
  -
    username: john
    password: pass
    vars: {playlist_id: 1}
  -
    username: paul
    password: pass
    vars: {}

urls:
  public:
    -
      path: /
      methods: [get]
    -
      path: /accounts/login/
      methods: [get]

  authentication:
    -
      path: /playlist/
      methods: [get, post]

  authorization:
    -
      path: /playlist/{playlist_id}/
      methods: [put, delete]
```

The complete example can be found under examples/ and it's a django app with some checks removed on purpose. Here is the
output of that:

```
/
 GET
     Allow anonymous (200) => OK

/accounts/login/
 GET
     Allow anonymous (200) => OK

/playlist/
 GET
     Deny anonymous (302) => OK
     Allow john (200) => OK
     Allow paul (200) => OK
 POST
     Deny anonymous (403) => OK
     Allow john (200) => OK
     Allow paul (200) => OK

/playlist/1/
 DELETE
     Allow john (200) => OK
     Deny paul (403) => OK
 PUT
     Allow john (200) => OK
     Deny paul (200) => FAILED

One or more functions have produced unexpected results...
```

## Usage
```bash
usage: fnval [-h] [-i INPUT]

optional arguments:
  -h, --help                    show this help message and exit
  -i INPUT, --input INPUT       app configuration file path
```

Using Playlists example:
```bash
python fnval -i examples/playlists/functions.yaml
```