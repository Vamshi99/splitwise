# Splitwise 
A django application which exposes APIs required for Splitwise, to manage expenses and settlements between users.

`Postman Collection file`:  Splitwise API.postman_collection.json (present in root directory)

`Docker Image Size`: 90MB 

## Design

#### Models: 

- User - Stores user details like name, email(unique)

- Group - Stores Group details like name, description

- GroupToUser - Intermediate model to store relation between user and group

- Expense - Stores Expense details like expense name, description, group id, payee user id, total amount

- ExpenseToUsers - Stores each user expense amount in the defined expense.

- Balance - Stores settlement related data like how much does one user owe the other.


## Environment Setup
Requirements:
- Docker
- Git

Run following commands to get the environment setup running: 
Get source code from the git repository and provide your git credentials as required
```sh
git clone https://github.com/Vamshi99/splitwise.git
```

Build Docker image from Dockerfile
```sh
cd splitwise/
docker-compose build
```

Start the docker container(in background) to run the django app. Django app will be running at localhost:5001

Note: You can change the port number in DockerFile if needed
```sh
docker-compose up -d
```


## Endpoint details:
API Type | API Endpoint | Function |
---------| ------------ | -------- |
GET | /users?id={user_id} | Get all the users details. Can take optional id parameter to fetch only required user details by giving user id
POST | /users | Create a new user given name and email details. Returns new user details
GET | /groups?id={group_id} | Get all the groups details. Can take optional id parameter to fetch only required group details by giving group id
POST | /groups | Create a new group given name and description details. Returns new group details
POST | /groups/users | Adds user to the group. Needs user_id and group_id in the body
GET | /groups/{group_id}/users | Get all the users in the given group id
POST | /expenses | Create a new expense in the group. Requires expense name, description, groupId, payeeId, amount and the userExpenseMap (Note: userExpenseMap contains each user contribution in the expense, the sum of these amounts should match the total expense amount)
GET | /settlements/{group_id}/{userID} | Get all the settlements amounts of a given user in the group. It returns has two maps which holds info on how much and to whom user is owed or owed to
POST | /settlements/payAmount/ | Payment to add between a sender and receiver with given amount.


