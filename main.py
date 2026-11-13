
e7fb6a98-2470-467f-a45a-f0a0d82923a6-0a71b51e-9082-4b92-a2ba-5e8c247f094b-main.zip
File

Pasted text(2).txt
Document
this is my complete project go through the complete project and explain me routes.py inside api folder first explain in detail for what it is being used in our project what is each endpoint doing theroticaally and then explain full code endpont by endpoint in detail 
this is routes.py code:




Complete explanation of api/routes.py
Let's understand this file from the perspective of your complete project, rather than just understanding FastAPI syntax.

Your routes.py file is one of the most important files in the backend because it acts as the API layer of your project. It connects the frontend, authentication system, database, AI agents, machine learning models, document-based chatbot, and dispute-management workflow.

I'll explain it in two major parts:

Theoretical understanding: Why routes.py exists, what role it plays, how API endpoints work, and what each endpoint does in your project.

Code-level understanding: Every endpoint, line by line, including the functions it calls, the data it receives, the data it returns, and why each operation is necessary.

I'll also distinguish between what routes.py does itself and what it delegates to other files. This distinction is important because the route functions mostly coordinate the project rather than implement all the business logic themselves.

1. What is routes.py, and why do we need it?
Your project appears to be an AI-powered toll dispute assessment and management system.

It handles several responsibilities:

User authentication and role-based access.

Displaying toll disputes that need investigation.

Calculating corrected toll charges.

Analysing the causes of toll disputes.

Estimating the effort required to resolve disputes.

Running a multi-agent AI assessment.

Allowing managers to approve or reject assessments.

Maintaining dispute records.

Answering questions using documents and dispute records.

Recording chat interactions for auditing.

All these functionalities need to communicate with the frontend.

For example, imagine your frontend has a Login page. When a user enters their username and password and clicks Login, the frontend needs to communicate with the Python backend.

The frontend cannot directly call a Python function such as sign_in_user().

Instead, it sends an HTTP request to an API endpoint.

That endpoint is defined in routes.py.

Understanding the communication
Frontend (UI)

Login page, dispute dashboard, chat interface, manager dashboard

HTTP requests and JSON responses

routes.py — API layer

Receives requests, validates access, calls backend functions, returns responses

AI / ML

Agents, LangGraph, prediction models, RAG

Database

Users, disputes, assessments, chat history

Business logic

Charge calculation, compensation, ranking

Security

Password hashing, authorization, sessions

A simple real-world analogy
Think of a restaurant.

Frontend = Customer.

routes.py = Waiter.

Database = Kitchen's stored inventory and order records.

AI agents = Specialists preparing and analysing the order.

Business logic = Recipes and calculation rules.

The customer doesn't directly enter the kitchen and prepare food. They give an order to the waiter.

Similarly, the frontend sends a request to routes.py, and routes.py coordinates the backend operations.

Therefore, the primary responsibility of routes.py is to act as the communication and coordination layer between the frontend and the backend services.

2. Understanding the structure of routes.py
Before studying individual endpoints, let's divide the file into logical sections.

Your routes.py has approximately 353 lines and contains the following sections:

Lines

Section

Responsibility

1–56

Imports

Importing dependencies and project functions

59–65

Initialization

Loading workflow, prediction facts and dispute queue

68–70

Router configuration

Public and authenticated routes

74–109

Authentication

Sign in and sign out

112–170

Dispute queue

List disputes and retrieve individual dispute details

174–202

Assessment

Start AI-powered dispute assessment

205–276

Dispute management

List disputes, submit decisions and inspect LLM calls

280–311

Chat assistant

Answer questions using documents and dispute records

314–326

Chat history and audit

Retrieve conversation records

330–345

Exception handling

Handle failed backend operations

348–352

FastAPI application

Create application and register routers and exception handlers

There are 11 API endpoints in this file and one additional helper function for handling failures.

Let's first understand some important concepts used throughout these endpoints.

3. Important FastAPI concepts used in this file
A. What is an API endpoint?
An API endpoint is a particular URL through which the frontend communicates with the backend to perform an operation.

For example:

@public_router.post("/auth/signin")
def sign_in_user(sign_in_request: SignInRequest):

Here:

/auth/signin is the endpoint URL.

POST is the HTTP method.

sign_in_user is the Python function executed when that endpoint receives a request.

SignInRequest specifies the expected request data.

If the backend runs at http://localhost:8000, the complete endpoint becomes:

http://localhost:8000/auth/signin
B. What are HTTP methods?
Your project uses two primary HTTP methods.

Method

Purpose

Example in your project

GET

Retrieve information

Get dispute queue

POST

Submit information or trigger an operation

Sign in, start assessment, submit decision

Think of it this way:

GET: I want to see something.

POST: I want to submit something or initiate an operation.

C. What is APIRouter?
Your code creates two routers:

public_router = APIRouter()

guarded_router = APIRouter(
    dependencies=[Depends(authorize_request)]
)

An APIRouter is used to group related endpoints.

Your project has two categories of endpoints.

1. public_router

No automatic authentication dependency
/auth/signin

/auth/signout

These endpoints do not automatically execute authorize_request through the router.

2. guarded_router

Authentication required
/queue

/queue/{dispute_reference}

/assessments

/disputes

/disputes/{assessment_id}/decision

/disputes/{assessment_id}/calls

/chat/ask

/chat/turns

/audit/chat-turns

These endpoints automatically require authentication through authorize_request.

Why do we need two routers?

Because users must be able to sign in before they have an authenticated session. If the login endpoint itself required an authenticated session, users could never log in.

Sign-out is also public at the router level, but it manually checks the session token inside its function.

D. What is Depends()?
FastAPI provides dependency injection through Depends().

For example:

guarded_router = APIRouter(
    dependencies=[Depends(authorize_request)]
)

This means:

Before executing an endpoint belonging to guarded_router, FastAPI executes authorize_request.

That function checks:

Whether the user provided a session token.

Whether the token exists in the database.

Whether the user's role is permitted to access the requested area.

If authentication fails, the endpoint is not executed.

Your code also defines:

SignedInUser = Annotated[
    dict,
    Depends(authorize_request)
]

This allows an endpoint to receive the authenticated user's account information directly.

For example:

def ask_toll_assistant(
    chat_request: ChatRequest,
    signed_in_user: SignedInUser
):

Here, signed_in_user contains information about the authenticated user, including username, display name and role.

FastAPI normally caches the same dependency result within a request, so the router-level and parameter-level uses do not necessarily execute the authentication function twice.

E. What are Pydantic schemas?
Your project has another important file:

api/
    routes.py
    schemas.py
schemas.py defines the structure of incoming requests and outgoing responses.

For example:

class SignInRequest(BaseModel):
    username: str
    password: str

This tells FastAPI that the login request must contain a username and password.

If the frontend sends:

{
    "username": "analyst01",
    "password": "mypassword"
}

FastAPI validates the request and creates a SignInRequest object.

You can then access:

sign_in_request.username
sign_in_request.password

Similarly, response_model controls the structure of the response returned by an endpoint.

For example:

@public_router.post(
    "/auth/signin",
    response_model=SignedInUserResponse
)

This ensures the response follows the structure defined by SignedInUserResponse.

Important: Schemas define the expected data structure; route functions implement the operations.

4. Initialization: What happens before endpoints execute?
Before the endpoint definitions, your code has an important initialization section.

Let's understand it first because almost every dispute-related endpoint depends on these variables.

Code
assessment_graph = build_workflow(
    config.CHECKPOINT_DATABASE_FILE
)

_facts_list = build_restatement_facts(
    nodes.restatement_model,
    nodes.restatement_feature_names,
    nodes.open_disputes
)

restatement_facts_by_reference = dict(
    zip(
        nodes.open_disputes[config.DISPUTE_REFERENCE_COLUMN],
        _facts_list
    )
)

_ranked_rows = rank_dispute_queue(
    nodes.open_disputes,
    nodes.tariff_schedules
)

for _row in _ranked_rows:
    _row.update(
        restatement_facts_by_reference[
            _row["dispute_reference"]
        ]
    )

dispute_queue = _ranked_rows

Let's understand this step by step.

Step 1: Build the AI workflow
assessment_graph = build_workflow(
    config.CHECKPOINT_DATABASE_FILE
)

This calls the build_workflow() function from:

agentic/graph.py
Your project uses LangGraph to execute a multi-agent dispute assessment workflow.

The workflow contains these ten nodes:

load_dispute_context

plan_assessment

assess_restatement_risk

identify_cause

check_tariff_charges

compose_dispute_assessment

request_manager_decision

draft_compensation_letter

draft_restated_statement

record_dispute_outcome

The graph defines how these nodes execute and how the workflow branches depending on the manager's decision.

It also uses SQLite checkpointing to save workflow state.

Why is this necessary?

Suppose an analyst starts an assessment.

The AI agents complete their investigation, but the workflow needs a manager's decision before finalizing the result.

The workflow must pause and remember everything it has calculated.

LangGraph checkpointing allows the project to resume that same workflow later instead of starting from the beginning.

Step 2: Generate restatement prediction facts
_facts_list = build_restatement_facts(
    nodes.restatement_model,
    nodes.restatement_feature_names,
    nodes.open_disputes
)

This uses the trained restatement prediction model.

The inputs are:

nodes.restatement_model: The trained ML model.

nodes.restatement_feature_names: The features expected by the model.

nodes.open_disputes: The open dispute dataset.

The function generates prediction-related facts for the disputes.

These include information such as:

Restatement probability.

Restatement band.

Other facts needed for the dispute queue.

The actual feature processing and prediction implementation is in tools/prediction_tools.py.

Step 3: Create a dictionary using dispute references
restatement_facts_by_reference = dict(
    zip(
        nodes.open_disputes[
            config.DISPUTE_REFERENCE_COLUMN
        ],
        _facts_list
    )
)

This is a very important operation.

Imagine your dataset contains:

Dispute reference

Restatement probability

TSD-DUB-0000001

0.85

TSD-DUB-0000002

0.45

TSD-DUB-0000003

0.92

Instead of searching through the entire dataset whenever a dispute is requested, your code creates a dictionary.

Conceptually:

{
    "TSD-DUB-0000001": {
        "restatement_probability": 0.85
    },
    "TSD-DUB-0000002": {
        "restatement_probability": 0.45
    },
    "TSD-DUB-0000003": {
        "restatement_probability": 0.92
    }
}

Now, given a dispute reference, the project can quickly retrieve its prediction facts.

Step 4: Rank the dispute queue
_ranked_rows = rank_dispute_queue(
    nodes.open_disputes,
    nodes.tariff_schedules
)

This calls the ranking function from:

tools/charge_tools.py
It prepares ranked dispute queue rows using the open dispute dataset and tariff schedules.

Step 5: Add ML prediction facts to every row
for _row in _ranked_rows:
    _row.update(
        restatement_facts_by_reference[
            _row["dispute_reference"]
        ]
    )

For every dispute:

Get its dispute reference.

Find its restatement prediction facts.

Add those facts to the existing queue row.

Finally:

dispute_queue = _ranked_rows

The complete queue is stored in memory.

Why is this done outside the endpoint functions?

Because the project prepares this information when the API module is initialized. The queue endpoint can then retrieve the already-prepared data instead of repeating the entire prediction and ranking process for every request.

One important implication: these values are not automatically refreshed on every GET request. They are based on the data loaded when the module initializes.

5. Endpoint 1 — User Sign In
Public endpoint POST

@public_router.post(
    "/auth/signin",
    response_model=SignedInUserResponse
)
def sign_in_user(sign_in_request: SignInRequest):

5.1 What is this endpoint used for theoretically?
This endpoint authenticates a user and creates an authenticated session.

Imagine your system has different users:

Toll Billing Analyst.

Revenue Assurance Manager.

Other authorized operational users.

Each user has credentials stored in the database.

When someone enters their username and password in the frontend, the frontend sends those credentials to this endpoint.

The backend verifies the credentials.

If they are correct, it generates a session token and returns the user's profile and permissions.

The frontend can then use this session token for subsequent API requests.

5.2 Complete code explanation
Step 1: Receive the login request

def sign_in_user(sign_in_request: SignInRequest):

sign_in_request contains the username and password supplied by the frontend.

Because it uses SignInRequest, FastAPI validates the request structure.

Step 2: Open a database session

with session_factory() as session:

This creates a database session using the session factory defined in:

persistence/database.py
A database session allows the application to communicate with the database.

The with statement ensures that the session is closed when the block finishes.

Step 3: Find the user account

account = fetch_user_account(
    session,
    UserAccount.username == sign_in_request.username
)

This calls fetch_user_account() from:

persistence/repository.py
Let's break it down:

session: Database connection/session.

UserAccount: SQLAlchemy database model.

UserAccount.username == sign_in_request.username: Condition to find the account.

Conceptually, it performs:

SELECT *
FROM user_accounts
WHERE username = 'analyst01';

If the account exists, its information is returned.

Otherwise, account becomes None.

Step 4: Check whether the account exists

if account is None:
    raise HTTPException(
        status_code=401,
        detail=config.SIGN_IN_FAILED_MESSAGE
    )

If the username does not exist, the API returns HTTP 401 Unauthorized.

Notice that the system uses a common login failure message rather than revealing whether the username or password was incorrect.

This is a security practice that helps prevent username enumeration.

Step 5: Hash the supplied password

hashed = hash_password(
    sign_in_request.password,
    account["password_salt"]
)

This is one of the most important security operations.

Your project does not simply compare the entered password with a plaintext password.

Instead, it uses password hashing.

The hash_password() function comes from:

access/password_security.py
The process is:

Receive the password entered by the user.

Retrieve the stored salt for that account.

Apply the configured password-hashing process.

Generate a hash.

Compare it with the stored password hash.

A salt is additional random data used during password hashing to make identical passwords produce different stored hashes.

Step 6: Compare password hashes securely

if not hmac.compare_digest(
    hashed,
    account["password_hash"]
):
    raise HTTPException(
        status_code=401,
        detail=config.SIGN_IN_FAILED_MESSAGE
    )

Why use hmac.compare_digest() instead of ==?

It performs a timing-resistant comparison designed to reduce timing side-channel leakage.

If the hashes do not match, authentication fails.

Step 7: Generate a session token

token = secrets.token_urlsafe(
    config.SESSION_TOKEN_BYTES
)

Once the credentials are verified, the application generates a new secure session token.

For example, conceptually:

XyZ123abc...random-token...
The actual token is generated randomly; this is only an illustration.

Why do we need it?

We do not want users to send their username and password with every request.

Instead, they send their session token to prove that they have authenticated.

Step 8: Save the session token

update_session_token(
    session,
    account["username"],
    token
)

This calls the repository function that updates the user's database record.

Conceptually:

UPDATE user_accounts
SET session_token = 'generated-token'
WHERE username = 'analyst01';

Your project stores one current session token per account. Logging in again replaces the previous token.

Step 9: Return user information

return {
    "username": account["username"],
    "display_name": account["display_name"],
    "role": account["role"],
    "session_token": token,
    "pages": config.ROLE_PAGE_ACCESS[account["role"]],
    "areas": config.ROLE_AREA_ACCESS[account["role"]]
}

This returns:

Field

Meaning

username

User's login username

display_name

User's display name

role

User's assigned role

session_token

Newly generated authentication token

pages

Frontend pages accessible to that role

areas

Backend functional areas accessible to that role

For example, an analyst and a manager may have different permissions.

The frontend can use pages to decide which screens to display, while the backend uses areas to enforce access restrictions.

Complete login flow
User enters credentials

Frontend sends username and password.

Find account

Backend queries user_accounts.

Verify password

Hash entered password and compare with stored hash.

Generate token

Create a secure random session token.

Save token

Update the user's database record.

Return response

Send profile, role, permissions and session token.

In simple words: This endpoint checks whether the user is genuine and, if authenticated, gives them a token that they can use to access protected features of the system.

6. Endpoint 2 — User Sign Out
Public endpoint POST

@public_router.post(
    "/auth/signout",
    response_model=SignedOutResponse
)
def sign_out_user(
    session_token: SessionTokenHeader = None
):

6.1 Theoretical purpose
This endpoint terminates the current authenticated session.

When a user clicks Logout, the frontend calls this endpoint.

The backend identifies the account associated with the session token and invalidates that token.

After logout, the old token cannot be used to access protected endpoints.

6.2 Code explanation
Step 1: Receive session token

session_token: SessionTokenHeader = None

Let's understand this custom type:

Earlier, your code defined:

SessionTokenHeader = Annotated[
    str | None,
    Header(alias=config.SESSION_TOKEN_HEADER)
]

This tells FastAPI to extract the session token from an HTTP request header.

For example, the request might contain:

X-Session-Token: abc123xyz
The actual header name comes from your configuration.

Step 2: Check whether the token was supplied

if not session_token:
    raise HTTPException(
        status_code=401,
        detail=config.SIGN_IN_REQUIRED_MESSAGE
    )

If the token is missing, the request is rejected.

Step 3: Open database session

with session_factory() as session:

Opens a database session.

Step 4: Find the account associated with the token

account = fetch_user_account(
    session,
    UserAccount.session_token == session_token
)

Here, the search condition is based on the session token instead of the username.

Conceptually:

SELECT *
FROM user_accounts
WHERE session_token = 'abc123xyz';

Step 5: Verify the token

if account is None:
    raise HTTPException(
        status_code=401,
        detail=config.SIGN_IN_REQUIRED_MESSAGE
    )

If the token does not correspond to an active account session, logout cannot proceed.

Step 6: Invalidate the token

update_session_token(
    session,
    account["username"],
    None
)

This is the actual logout operation.

It changes the user's session token to None.

Conceptually:

UPDATE user_accounts
SET session_token = NULL
WHERE username = 'analyst01';

Now the previous token is no longer valid.

Step 7: Return confirmation

return {
    "username": account["username"],
    "signed_out": True
}

The response confirms that the user has signed out.

In simple words: Sign-in creates a session token; sign-out invalidates that session token.

7. Endpoint 3 — Get Dispute Queue
Authenticated endpoint GET

@guarded_router.get(
    "/queue",
    response_model=list[QueueRow]
)
def list_dispute_queue(direction: DirectionFilter):

7.1 Theoretical purpose
This endpoint displays the list of open toll disputes that need investigation.

Imagine the company has received 1,000 toll dispute records.

The analyst needs to see:

Which disputes are pending investigation?

Which disputes have incorrect billing?

Which disputes may need a corrected statement?

How much money is involved?

Which disputes should be prioritized?

Instead of displaying every raw dataset column, this endpoint returns a prepared and ranked queue.

It also supports filtering based on the direction of the billing discrepancy.

7.2 Understanding DirectionFilter
In schemas.py, you have:

DirectionFilter = Literal[
    tuple(config.QUEUE_DIRECTION_OPTIONS)
]

This restricts the allowed values to those configured in your project.

For example, the conceptual possibilities are:

All disputes.

Customer overcharged.

Customer undercharged.

The exact strings are defined in config.py.

7.3 Code explanation
def list_dispute_queue(direction: DirectionFilter):

The endpoint accepts a required query parameter called direction.

For example:

GET /queue?direction=ALL
Step 1: Check whether all disputes are requested

if direction == config.QUEUE_DIRECTION_ALL:
    return dispute_queue

If the user requests all disputes, the entire precomputed queue is returned.

Step 2: Otherwise filter the queue

return [
    r for r in dispute_queue
    if r["direction"] == direction
]

This is Python list comprehension.

Let's break it down:

for r in dispute_queue: Iterate through every dispute.

r["direction"] == direction: Check its discrepancy direction.

Return only the matching rows.

Equivalent longer code:

filtered_rows = []

for r in dispute_queue:
    if r["direction"] == direction:
        filtered_rows.append(r)

return filtered_rows

7.4 What does the response contain?
Your QueueRow schema defines these fields:

Field

Meaning

dispute_reference

Unique dispute identifier

billing_centre

Billing centre handling the dispute

billed_tariff

Tariff originally applied

entitled_tariff

Tariff the customer was entitled to

amount_billed_eur

Amount originally billed

restated_charge_eur

Recalculated charge

difference_eur

Difference between original and corrected charge

money_at_stake_eur

Financial amount involved

direction

Direction of discrepancy

restatement_warranted

Whether a corrected statement is warranted

restatement_probability

ML-predicted probability

restatement_band

ML prediction category

In simple words: This endpoint supplies the analyst dashboard with a ranked list of open disputes and allows the user to filter them by discrepancy direction.

8. Endpoint 4 — Get Individual Dispute Details
Authenticated endpoint GET

@guarded_router.get(
    "/queue/{dispute_reference}",
    response_model=DisputeDetailResponse
)
def get_dispute_detail(dispute_reference: str):

8.1 Theoretical purpose
The previous endpoint returns a summary of multiple disputes.

But when an analyst clicks one particular dispute, they need much more detailed information.

For example, the queue may show:

TSD-DUB-0000001
Amount billed: EUR 150
Restated charge: EUR 120
Difference: EUR 30
The analyst now wants to understand:

What happened with this customer's toll passages?

What do the customer contact notes say?

Was the correct tariff applied?

What should the corrected charge be?

Is compensation required?

How complicated will the investigation be?

This endpoint gathers all that information.

8.2 Code explanation
Step 1: Receive dispute reference

def get_dispute_detail(dispute_reference: str):

The dispute reference is passed through the URL.

For example:

GET /queue/TSD-DUB-0000001
FastAPI extracts the reference and passes it to the function.

Step 2: Validate dispute existence

if dispute_reference not in restatement_facts_by_reference:
    raise HTTPException(
        status_code=404,
        detail=config.DISPUTE_NOT_IN_QUEUE_MESSAGE.format(
            dispute_reference=dispute_reference
        )
    )

Remember the dictionary we created during initialization?

restatement_facts_by_reference

It contains prediction facts indexed by dispute reference.

If the requested reference does not exist, the endpoint returns 404 Not Found.

Step 3: Retrieve dispute profile

profile = fetch_dispute_profile(
    nodes.open_disputes,
    dispute_reference
)

This calls:

tools/dispute_data_tools.py
It retrieves the original dispute record from the loaded open-disputes dataset.

The profile contains the information needed for further calculations, such as billing, tariff and passage information.

Step 4: Clean missing values

cleaned_profile = {
    k: (None if pd.isna(v) else v)
    for k, v in profile.items()
}

Let's understand this carefully.

pd.isna(v) checks whether a value is missing.

For example:

profile = {
    "account_number": "ACC101",
    "billing_centre": "Dublin",
    "vehicle_class": float("nan")
}

After cleaning:

cleaned_profile = {
    "account_number": "ACC101",
    "billing_centre": "Dublin",
    "vehicle_class": None
}

Why?

Pandas uses NaN for missing numerical values.

But JSON does not have a standard NaN value. Converting it to Python None allows it to be represented as JSON null.

Step 5: Retrieve customer contact notes

note_texts = fetch_dispute_notes(
    nodes.open_dispute_notes,
    dispute_reference
)

This retrieves the notes associated with the dispute.

For example, they might contain information about:

Customer complaints.

Incorrect vehicle classification.

Duplicate toll passages.

Payments not being applied.

These notes are later used for cause analysis.

Step 6: Retrieve existing ML restatement facts

restatement = restatement_facts_by_reference[
    dispute_reference
]

This retrieves the ML prediction generated during initialization.

It avoids running the same prediction again.

Step 7: Predict the cause of the dispute

cause = build_cause_facts(
    nodes.cause_model,
    note_texts
)

This uses the cause prediction model.

Inputs:

Trained cause model.

Customer contact notes.

The objective is to identify the likely dispute category from the available notes.

For example, the cause could be related to duplicate passages or payments not being applied.

The exact categories are determined by the project's model and its configuration.

Step 8: Measure toll passages

passages = measure_passages(profile)

This calls a function from:

tools/charge_tools.py
It processes the passage information associated with the dispute.

The purpose is to establish the toll passages that need to be considered when calculating the corrected charge.

Step 9: Build charge pieces

pieces = build_charge_pieces(
    profile,
    nodes.tariff_schedules
)

This breaks the dispute's toll charges into individual charge components.

Why?

Because different passages may belong to different tariff schedules or charging periods.

The system needs to identify which tariff applies to each component.

Step 10: Calculate the corrected charge

restated = compute_restated_charge(
    pieces,
    passages
)

This calculates the corrected toll charge using the identified charge components and passage information.

It returns a dictionary containing the recalculated charge information.

Step 11: Extract calculated results

priced_pieces = restated["pieces"]

restated_charge_eur = (
    restated["restated_charge_eur"]
)

We separate:

priced_pieces: Individual priced components.

restated_charge_eur: Total corrected charge.

Step 12: Compare corrected charge with billed charge

comparison = compare_with_billed(
    profile,
    restated_charge_eur
)

This compares what the customer was originally charged with what they should have been charged.

For example:

Description

Amount

Original billed amount

EUR 150

Corrected amount

EUR 120

Difference

EUR 30

This comparison helps determine whether the statement should be corrected.

Step 13: Calculate compensation

compensation = compute_compensation(
    profile,
    nodes.commitment_payments
)

This checks the service commitments and associated payment information.

It determines whether the organisation breached any commitments and whether compensation is due.

Step 14: Identify relevant tariff schedules

relevant_tariffs = list(
    dict.fromkeys(
        [p["tariff"] for p in priced_pieces]
        + [profile[config.BILLED_TARIFF_COLUMN]]
    )
)

This is a slightly advanced Python expression.

Let's divide it.

First:

[p["tariff"] for p in priced_pieces]

Extracts the tariff name from every priced charge component.

Next:

+ [profile[config.BILLED_TARIFF_COLUMN]]

Adds the originally billed tariff.

Finally:

dict.fromkeys(...)

Removes duplicate tariff names while preserving their insertion order.

Then:

schedules_dict = {
    t: nodes.tariff_schedules[t]
    for t in relevant_tariffs
    if t in nodes.tariff_schedules
}

This retrieves only the relevant tariff schedules.

Why not send every tariff schedule?

Because the AI agent only needs the schedules relevant to the dispute being investigated.

Step 15: Create the charge dictionary

charge = {
    "tariff_schedules": schedules_dict,
    "passages": passages,
    "pieces": priced_pieces,
    "comparison": comparison,
    "compensation": compensation
}

This combines all charge-related information into one dictionary.

It makes the information easier to return to the frontend and reuse in the assessment process.

Step 16: Estimate resolution effort

effort = estimate_resolution_effort(
    nodes.effort_model,
    nodes.effort_feature_names,
    profile,
    restatement["restatement_band"],
    cause["dispute_category"],
    priced_pieces,
    comparison["money_at_stake_eur"]
)

This calls the resolution-effort prediction function.

It uses the trained effort model to estimate:

How many hours are needed to resolve the dispute.

Whether senior analyst review is required.

Notice that it uses several inputs:

Effort prediction model.

Feature schema.

Dispute profile.

Restatement prediction band.

Predicted dispute category.

Charge components.

Financial amount at stake.

This is an example of how your project combines different ML predictions and business calculations.

Step 17: Return complete dispute details

return {
    "profile": cleaned_profile,
    "note_texts": note_texts,
    "restatement": restatement,
    "cause": cause,
    "charge": charge,
    "effort": effort
}

The response contains six major sections.

Individual dispute detail response

profile

Original dispute information.

note_texts

Customer contact notes.

restatement

ML prediction about whether the statement should be corrected.

cause

Predicted reason for the dispute.

charge

Passage analysis, tariffs, corrected charges, comparison and compensation.

effort

Predicted resolution time and senior-review requirement.

In simple words: This endpoint performs the preliminary investigation of an individual toll dispute by combining original data, customer notes, ML predictions and financial calculations. It returns the complete information needed before starting the AI assessment workflow.

9. Endpoint 5 — Start Dispute Assessment
Authenticated endpoint POST

@guarded_router.post(
    "/assessments",
    response_model=TollDisputeResponse,
    status_code=201
)
def start_dispute_assessment(
    assessment_request: AssessmentRequest,
    signed_in_user: SignedInUser,
    request: Request
):

This is one of the most important endpoints in your entire project.

9.1 Theoretical purpose
Until now, we have seen how the system displays dispute information and calculates preliminary facts.

But the actual assessment requires more than simply calculating numbers.

The system needs to investigate the dispute using multiple AI agents.

For example, an analyst selects a dispute and provides an instruction:

Investigate whether the customer was charged under
the wrong tariff and determine whether compensation
is required.
The system then:

Loads the dispute information.

Creates an investigation plan.

Assesses the probability of a corrected statement.

Identifies the likely cause.

Checks tariff charges.

Generates an assessment report.

Recommends a decision.

Pauses for a manager's decision.

This entire process is managed through LangGraph.

9.2 Code explanation
Step 1: Extract dispute reference

dispute_ref = assessment_request.dispute_reference

The request contains:

dispute_reference

analyst_request

These fields are defined in AssessmentRequest inside schemas.py.

For example:

{
    "dispute_reference": "TSD-DUB-0000001",
    "analyst_request": "Investigate the incorrect tariff applied to this customer."
}

Step 2: Validate dispute reference

if dispute_ref not in restatement_facts_by_reference:
    raise HTTPException(
        status_code=404,
        detail=config.DISPUTE_NOT_IN_QUEUE_MESSAGE.format(
            dispute_reference=dispute_ref
        )
    )

The system checks whether the dispute exists in the open dispute queue.

If it doesn't exist, it returns 404.

Step 3: Generate a unique thread ID

thread_id = (
    f"{dispute_ref}-"
    f"{uuid.uuid4().hex[:config.IDENTIFIER_HEX_LENGTH].upper()}"
)

This is very important for understanding LangGraph.

What is a thread ID?

A thread ID uniquely identifies a particular workflow execution.

For example:

TSD-DUB-0000001-A82F31
The first portion identifies the dispute.

The second portion is a randomly generated identifier.

Why do we need it?

Suppose an analyst starts an assessment for a dispute.

The workflow performs several operations and then pauses because it needs manager approval.

Later, the manager submits a decision.

How does the system know which paused workflow to resume?

It uses the thread ID.

Each workflow execution has its own thread ID, allowing the application to maintain separate execution states.

Step 4: Store the thread ID in the request state

request.state.opened_thread_id = thread_id

This attaches the thread ID to the current HTTP request.

Why?

It becomes useful if the workflow fails.

Your exception handler can retrieve this ID and identify which workflow was affected.

We'll understand this when we reach report_failed_request().

Step 5: Prepare initial workflow state

initial_state = {
    "dispute_reference": dispute_ref,
    "analyst_request": assessment_request.analyst_request,
    "analyst_id": signed_in_user["username"],
    "thread_id": thread_id,
    "llm_call_log": []
}

This dictionary contains the initial information required by the LangGraph workflow.

Let's understand every field:

Field

Purpose

dispute_reference

Which dispute must be investigated

analyst_request

What the analyst wants investigated

analyst_id

Who initiated the assessment

thread_id

Unique workflow execution identifier

llm_call_log

Initially empty list for recording LLM calls

This dictionary is the initial state passed into LangGraph.

Step 6: Execute the workflow

assessment_graph.invoke(
    initial_state,
    config={
        "configurable": {
            "thread_id": thread_id
        }
    }
)

This is the most important line of this endpoint.

assessment_graph was created earlier using build_workflow().

.invoke() starts executing the workflow.

The initial state is passed to the first node.

The execution follows the graph defined in:

agentic/graph.py
Let's understand its execution.

LangGraph assessment workflow

1. Load dispute context

Retrieve profile, notes and ML prediction facts

2. Plan assessment

Planning agent creates investigation plan

3. Assess restatement risk

Restatement assessment agent

4. Identify cause

Cause identification agent

5. Check tariff charges

Calculate charges and obtain tariff advice

6. Compose dispute assessment

Combine findings and save pending assessment

7. Request manager decision

Workflow pauses here
Wait for human approval or rejection

Notice that the last three nodes are not executed yet.

They are executed after the manager submits a decision.

The thread_id in the configuration tells LangGraph which execution to checkpoint.

Step 7: Retrieve the workflow checkpoint

checkpoint = assessment_graph.get_state(
    {"configurable": {"thread_id": thread_id}}
)

After the workflow pauses, this retrieves the saved workflow state.

It contains the information accumulated during execution.

Step 8: Retrieve assessment ID

assessment_id = checkpoint.values["assessment_id"]

Inside the first LangGraph node, load_dispute_context_node, your project generates a unique assessment ID.

For example:

ASM-123456
The actual format comes from your configuration.

The assessment ID identifies the assessment record, whereas the thread ID identifies the workflow execution.

These two IDs serve different purposes.

Step 9: Retrieve the saved assessment from the database

with session_factory() as session:
    records = fetch_dispute_records(
        session,
        TollDispute.assessment_id == assessment_id
    )

This queries the database for the assessment record.

The assessment was inserted into the toll_disputes table by the compose_dispute_assessment_node.

fetch_dispute_records() also joins information from the agent run and manager decision tables.

Step 10: Return the assessment

return records[0]

The endpoint returns the first matching assessment record.

Because this is a newly generated unique assessment ID, the expected result is one record.

The HTTP response status is 201 Created.

9.3 Important distinction: assessment_id vs run_id vs thread_id
This is a common interview question.

ID

Purpose

assessment_id

Identifies the dispute assessment record

run_id

Identifies the AI agent execution run

thread_id

Identifies the LangGraph execution/checkpoint thread

They are related, but they are not interchangeable.

In simple words: This endpoint starts the complete AI-powered dispute investigation, saves its findings, and pauses the workflow until a manager makes a decision.

10. Endpoint 6 — List Disputes
Authenticated endpoint GET

@guarded_router.get(
    "/disputes",
    response_model=list[TollDisputeResponse]
)
def list_disputes(
    status_value: list[DisputeStatusValue] = Query(...)
):

10.1 Theoretical purpose
This endpoint retrieves previously generated dispute assessments based on their status.

Remember, your project has a separate table containing the assessments generated by the AI workflow.

Not every dispute in the open dispute queue has an assessment.

This endpoint retrieves those assessments that have already been created.

For example, the frontend may want to display:

Assessments awaiting manager decisions.

Approved assessments.

Rejected assessments.

Completed dispute settlements.

The actual status values are defined in config.py.

10.2 Code explanation
Step 1: Receive status filters

status_value: list[DisputeStatusValue] = Query(...)

This means the endpoint accepts one or more status values through query parameters.

For example, conceptually:

GET /disputes?status_value=PENDING
Multiple values can also be provided:

GET /disputes?status_value=PENDING&status_value=COMPLETED
DisputeStatusValue restricts the values to those defined in the project's configuration.

Query(...) means the query parameter is required.

Step 2: Open database session

with session_factory() as session:

Creates a database session.

Step 3: Fetch matching records

records = fetch_dispute_records(
    session,
    TollDispute.status.in_(status_value)
)

This is SQLAlchemy filtering.

.in_() checks whether a column value belongs to a list of values.

Conceptually:

SELECT *
FROM toll_disputes
WHERE status IN ('PENDING', 'COMPLETED');

The actual repository query also joins agent run and manager decision details.

Step 4: Return the records

return records

The returned records follow the TollDisputeResponse schema.

This includes assessment details, AI findings, recommended decisions and manager decision information where available.

In simple words: This endpoint retrieves existing AI-generated dispute assessments according to their current status.

11. Endpoint 7 — Submit Manager Decision
Authenticated endpoint POST

@guarded_router.post(
    "/disputes/{assessment_id}/decision",
    response_model=TollDisputeResponse
)
def submit_manager_decision(
    assessment_id: str,
    decision_request: DecisionRequest,
    signed_in_user: SignedInUser
):

11.1 Theoretical purpose
This endpoint implements the human approval stage of your AI-powered system.

Your AI agents investigate the dispute and recommend an action.

However, the system does not automatically finalize the dispute based solely on the AI recommendation.

A Revenue Assurance Manager must review the assessment and make the final decision.

Possible decisions are defined in:

config.DECISION_OPTIONS

In your workflow, the decision branches include:

Uphold the original statement.

Restate the statement.

Restate the statement and provide compensation.

The manager submits the decision and a reason.

The backend resumes the paused LangGraph workflow and finalizes the appropriate settlement.

11.2 Code explanation
Step 1: Retrieve assessment ID

assessment_id: str

The assessment ID is provided in the URL.

For example:

POST /disputes/ASM-123456/decision
Step 2: Receive decision information

decision_request: DecisionRequest

This request contains:

class DecisionRequest(BaseModel):
    decision: Literal[tuple(config.DECISION_OPTIONS)]
    decision_reason: str = Field(
        min_length=config.DECISION_REASON_MINIMUM_CHARACTERS
    )

The manager must provide:

The selected decision.

A reason explaining the decision.

Pydantic validates the input before the endpoint executes.

Step 3: Receive authenticated manager information

signed_in_user: SignedInUser

This gives the endpoint information about the currently authenticated user.

The system needs this to know who is making the decision.

Step 4: Retrieve the assessment

with session_factory() as session:
    records = fetch_dispute_records(
        session,
        TollDispute.assessment_id == assessment_id
    )

This searches for the assessment in the database.

Step 5: Check whether the assessment exists

if not records:
    raise HTTPException(
        status_code=404,
        detail=config.ASSESSMENT_NOT_FOUND_MESSAGE
    )

If the assessment doesn't exist, return 404.

Step 6: Get the assessment record

record = records[0]

Extract the matching assessment.

Step 7: Prevent analysts from approving their own assessments

if record["analyst_id"] == signed_in_user["username"]:
    raise HTTPException(
        status_code=403,
        detail=config.OWN_ASSESSMENT_REFUSED_MESSAGE
    )

This is a very important business rule.

Imagine:

Analyst A investigates a dispute.

Analyst A recommends restating the statement.

Analyst A then tries to approve their own recommendation.

Your system prevents this.

The manager deciding the assessment must be a different user from the analyst who created it.

This helps maintain separation of duties and reduces conflicts of interest.

Step 8: Check whether the assessment is still pending

if record["status"] != config.DISPUTE_STATUS_PENDING:
    raise HTTPException(
        status_code=409,
        detail=config.ALREADY_DECIDED_MESSAGE
    )

Why?

Because an assessment that has already been decided should not be processed again.

HTTP 409 means Conflict.

For example, if the assessment is already completed, the manager cannot submit another decision.

Step 9: Retrieve the paused workflow state

checkpoint = assessment_graph.get_state(
    {"configurable": {"thread_id": record["thread_id"]}}
)

This retrieves the LangGraph checkpoint associated with the assessment.

Remember the thread ID?

It allows the application to find the exact workflow that was paused earlier.

Step 10: Check for an existing in-progress decision

held_decision = (
    checkpoint.values.get("manager_decision") or {}
).get("decision")

This retrieves any manager decision already present in the workflow state.

Why is this necessary?

Imagine a manager submits a decision and the workflow starts processing it.

But before the workflow finishes, another request attempts to submit a different decision.

The application checks whether a decision has already been recorded in the workflow state.

Step 11: Prevent conflicting decisions

if (
    held_decision is not None
    and held_decision != decision_request.decision
):
    raise HTTPException(
        status_code=409,
        detail=config.DECISION_IN_PROGRESS_MESSAGE.format(
            decision=held_decision
        )
    )

If another decision is already being processed and it differs from the new decision, the request is rejected.

This is a consistency check.

Step 12: Prepare manager decision payload

resume_payload = {
    "decision": decision_request.decision,
    "decided_by": signed_in_user["display_name"],
    "decided_by_role": signed_in_user["role"],
    "decision_reason": decision_request.decision_reason
}

This dictionary contains the decision information that will be passed into the paused workflow.

It contains:

What decision was made.

Who made it.

The manager's role.

Why the decision was made.

Step 13: Resume the LangGraph workflow

assessment_graph.invoke(
    Command(resume=resume_payload),
    config={
        "configurable": {
            "thread_id": record["thread_id"]
        }
    }
)

This is the key operation.

Earlier, the workflow was paused at the manager decision node.

Now:

Command(resume=resume_payload)

provides the human decision and resumes the workflow.

The graph checks the decision and follows the corresponding branch.

Manager decision branches

Manager decision received

Uphold statement

Go directly to record dispute outcome.

Restate statement

Draft corrected statement, then record outcome.

Restate and compensate

Draft compensation letter, draft corrected statement, then record outcome.

Record dispute outcome and finalize workflow

Step 14: Retrieve updated assessment

with session_factory() as session:
    updated_records = fetch_dispute_records(
        session,
        TollDispute.assessment_id == assessment_id
    )

After the workflow completes, the endpoint retrieves the updated assessment record.

Step 15: Return updated record

return updated_records[0]

The response now includes the manager's decision and the finalized settlement information, where applicable.

In simple words: This endpoint allows a manager to review an AI-generated assessment, submit an independent decision, resume the paused workflow and finalize the dispute outcome.

12. Endpoint 8 — Get LLM Call Budget
Authenticated endpoint GET

@guarded_router.get(
    "/disputes/{assessment_id}/calls",
    response_model=CallBudgetResponse
)
def get_call_budget(assessment_id: str):

12.1 Theoretical purpose
Your project uses multiple AI agents.

Every time an agent calls a language model, the system records information about that call.

For example:

Which agent made the call?

Which model was used?

How many characters were sent in the prompt?

How many characters were returned?

How much time did the call take?

Why is this important?

AI calls have operational costs and execution time.

If a dispute assessment requires too many language model calls, the system may become slower and more expensive.

This endpoint provides an audit of those calls.

12.2 Code explanation
Step 1: Receive assessment ID

def get_call_budget(assessment_id: str):

The assessment ID comes from the URL.

Step 2: Retrieve the assessment record

with session_factory() as session:
    records = fetch_dispute_records(
        session,
        TollDispute.assessment_id == assessment_id
    )

This searches the database for the corresponding assessment.

Step 3: Validate assessment existence

if not records:
    raise HTTPException(
        status_code=404,
        detail=config.ASSESSMENT_NOT_FOUND_MESSAGE
    )

If no assessment exists, return 404.

Step 4: Extract the assessment record

record = records[0]

Step 5: Retrieve its run ID

The record contains:

record["run_id"]

This identifies the AI agent execution run.

Remember:

Assessment ID identifies the assessment.

Run ID identifies the agent execution.

Step 6: Fetch LLM call records

with session_factory() as session:
    calls = fetch_llm_calls(
        session,
        record["run_id"]
    )

This retrieves the recorded language model calls for that run from the llm_calls table.

Step 7: Count the calls

call_count = len(calls)

For example:

calls = [
    {"agent_name": "Planning Agent"},
    {"agent_name": "Risk Agent"},
    {"agent_name": "Cause Agent"},
    {"agent_name": "Tariff Agent"}
]

Then:

call_count = 4

Step 8: Calculate total latency

total_latency = sum(
    c["latency_milliseconds"]
    for c in calls
)

Suppose the recorded latencies are:

Agent

Latency

Planning

1,000 ms

Risk

1,500 ms

Cause

800 ms

Tariff

1,200 ms

Total:

1000
+
1500
+
800
+
1200
=
4500
 ms
1000+1500+800+1200=4500 ms
Therefore, total recorded LLM latency is 4.5 seconds.

This is the sum of the individual call latencies, not necessarily the total wall-clock duration of the workflow.

Step 9: Calculate expected call count

expected_call_count = (
    config.LLM_CALLS_BY_DECISION[record["decision"]]
    if record.get("decision")
    else config.LLM_CALLS_BEFORE_DECISION
)

This uses a conditional expression.

It means:

If the assessment already has a decision, retrieve the expected call count for that decision.

Otherwise, use the expected number of calls before a decision.

Why does the expected count depend on the decision?

Because different manager decisions can trigger different workflow branches.

For example:

Upholding the statement requires fewer post-decision agent operations.

Restating and compensating requires additional document-generation operations.

The exact expected counts are configured in config.py.

Step 10: Return call metrics

return {
    "assessment_id": assessment_id,
    "run_id": record["run_id"],
    "call_count": call_count,
    "expected_call_count": expected_call_count,
    "total_latency_milliseconds": total_latency,
    "calls": calls
}

The response includes the individual call records and aggregate metrics.

In simple words: This endpoint tracks how many LLM calls were made during an assessment, how long they took, and how they compare with the expected call budget.

13. Endpoint 9 — Ask Toll Assistant
Authenticated endpoint POST

@guarded_router.post(
    "/chat/ask",
    response_model=ChatResponse
)
def ask_toll_assistant(
    chat_request: ChatRequest,
    signed_in_user: SignedInUser
):

13.1 Theoretical purpose
This endpoint implements the conversational assistant in your project.

Your system has a knowledge base containing documents related to toll operations.

For example:

Toll statement dispute policies.

Tariff schedules.

Customer service guides.

Duplicate passage guides.

Payment-related documentation.

Past dispute case studies.

Instead of making the user manually search through all these documents, the assistant allows them to ask questions in natural language.

For example:

What happens if a customer is charged under
the wrong vehicle tariff?
The system retrieves relevant document passages and uses an LLM to generate an answer.

This is called Retrieval-Augmented Generation (RAG).

But your chatbot has another capability.

If someone asks:

What is the current status of dispute
TSD-DUB-0000001?
The system recognizes that this is a dispute-status question and retrieves information from the actual dispute records instead of relying on document retrieval.

So, your chatbot has two important information sources:

Knowledge documents through RAG.

Live dispute assessment records through the database.

13.2 Code explanation
Step 1: Receive the user's question

chat_request: ChatRequest

The schema is:

class ChatRequest(BaseModel):
    question: str = Field(
        min_length=config.CHAT_QUESTION_MINIMUM_CHARACTERS
    )

This ensures the question satisfies the configured minimum length.

Step 2: Get the user's conversation history

with session_factory() as session:
    conv = recall_conversation(
        session,
        signed_in_user["username"],
        chat_request.question
    )

This calls:

chat/conversation_memory.py
Why?

Because your assistant supports conversational context.

Imagine this conversation:

User:

What is the duplicate passage policy?
Assistant:

The policy explains how duplicate toll passages are investigated.
User:

What happens if it is confirmed?
The second question doesn't explicitly mention duplicate passages.

But the assistant should understand that "it" refers to the previous topic.

recall_conversation() retrieves previous questions and answers and creates:

history_text: Previous conversation in readable form.

search_text: Previous questions combined with the current question.

This helps the retrieval process understand the context.

Step 3: Generate an answer using documents

reply = answer_from_documents(
    nodes.knowledge_collection,
    chat_request.question,
    conv
)

This is the main RAG operation.

It calls:

chat/toll_assistant.py
Let's understand what happens inside that function.

It searches the ChromaDB knowledge collection for relevant document chunks.

It searches using both the current question and conversation context.

It removes duplicate chunks and ranks the retrieved passages.

It loads the published tariff schedules.

It constructs a prompt containing the conversation, question and retrieved passages.

It calls the language model.

It asks the model to classify the question into one of five categories.

It extracts the answer and dispute reference where applicable.

It checks relevance and applies refusal rules.

The five question categories are:

Category

Purpose

TARIFFS

Questions about published tariff rates and contract terms

DISPUTE RULES

Questions about billing and dispute procedures

CUSTOMER ADVICE

Questions about customer actions and services

DISPUTE STATUS

Questions about a particular dispute

OUT OF SCOPE

Questions not supported by the knowledge base

The exact category strings come from your configuration.

Step 4: Check whether this is a dispute-status question

if reply["question_type"] == config.CHAT_TYPE_DISPUTE_STATUS:

This is where your chatbot becomes more than a basic document chatbot.

If the question is about a particular dispute, the system must retrieve its actual status.

Step 5: Retrieve dispute status from the database

with session_factory() as session:
    status_reply = answer_dispute_status(
        session,
        nodes.open_disputes,
        signed_in_user["role"],
        reply["dispute_reference"]
    )

This calls:

chat/dispute_status_answer.py
The function checks:

Whether the dispute reference is valid.

Whether an assessment exists.

What its current status is.

What information the user's role is permitted to see.

An important security feature is that the response depends on the user's role.

For users without financial-figure permissions, the system returns a status-oriented response and hides the financial figures.

For authorized roles, it can return detailed financial information, including:

Original billed amount.

Corrected amount.

Difference.

Compensation.

Restatement probability.

Cause category.

Estimated effort.

Manager decision.

Settlement information.

Step 6: Replace the preliminary answer with the database answer

reply["answer"] = status_reply["answer"]
reply["source_documents"] = status_reply["source_documents"]
reply["was_refused"] = status_reply["was_refused"]

Why replace these fields?

Because the earlier RAG function only classified the question and identified its dispute reference.

The actual dispute information must come from the database, not from general documents.

So, this step replaces the preliminary response with the role-appropriate database response.

Step 7: Convert source document names into a string

source_docs_str = ", ".join(
    reply["source_documents"]
)

Suppose the source documents are:

[
    "Toll-Statement-Disputes-Policy.pdf",
    "Guide-Duplicate-Passages.pdf"
]

The result becomes:

Toll-Statement-Disputes-Policy.pdf, Guide-Duplicate-Passages.pdf
Why?

Because your database's ChatTurn model stores the source documents as a string.

Step 8: Save the conversation in the database

with session_factory() as session:
    insert_chat_turn(session, {
        "username": signed_in_user["username"],
        "user_role": signed_in_user["role"],
        "question_text": chat_request.question,
        "question_type": reply["question_type"],
        "dispute_reference": reply["dispute_reference"],
        "answer_text": reply["answer"],
        "source_documents": source_docs_str,
        "closest_distance": reply["closest_distance"],
        "was_refused": reply["was_refused"]
    })

This stores the interaction in the chat_turns table.

Why do we store it?

To maintain conversation history.

To provide context for future questions.

To support compliance auditing.

To track which sources were used.

To record whether the assistant refused a question.

Notice that closest_distance is also recorded.

This is the distance returned by the document retrieval process. In your ChromaDB-based implementation, it provides a measure of how closely the retrieved content matches the query.

Step 9: Return the final reply

return reply

The response follows the ChatResponse schema.

It includes:

Question category.

Dispute reference, if identified.

Final answer.

Source documents.

Whether the answer was refused.

Complete chatbot flow
User asks a question

Retrieve conversation history

RAG document retrieval + LLM classification

What type of question is it?

Document question

Use retrieved document-based answer, subject to relevance and refusal checks.

Dispute status

Fetch actual dispute records and apply role-based information restrictions.

Save question and answer in chat history

Return final answer to frontend

In simple words: This endpoint powers your Toll Assistant. It answers questions using the organisation's documents, retrieves real dispute information when necessary, respects user permissions and stores every interaction for future context and auditing.

14. Endpoint 10 — Get Own Chat History
Authenticated endpoint GET

@guarded_router.get(
    "/chat/turns",
    response_model=list[ChatTurnResponse]
)
def list_own_chat_turns(
    signed_in_user: SignedInUser,
    turn_limit: int = Query(
        ge=1,
        le=config.CHAT_AUDIT_MAX_ROWS
    )
):

14.1 Theoretical purpose
This endpoint retrieves the chat interactions of the currently logged-in user.

For example, suppose an analyst previously asked:

What is the duplicate passage policy?
Then they asked:

What happens if the customer has already paid?
The frontend can call this endpoint to display the user's previous questions and answers.

This is different from the chatbot's internal recall_conversation() function.

recall_conversation() prepares context for the LLM.

/chat/turns returns the user's stored conversation records to the frontend.

14.2 Code explanation
Step 1: Receive authenticated user

signed_in_user: SignedInUser

This contains the currently authenticated account information.

Step 2: Accept a turn limit

turn_limit: int = Query(
    ge=1,
    le=config.CHAT_AUDIT_MAX_ROWS
)

This controls how many records can be returned.

ge=1 means greater than or equal to 1.

le=config.CHAT_AUDIT_MAX_ROWS means less than or equal to the configured maximum.

For example, if the maximum is 100:

10 is valid.

50 is valid.

0 is invalid.

101 is invalid.

Step 3: Retrieve chat history

with session_factory() as session:
    turns = fetch_chat_turns(
        session,
        ChatTurn.username == signed_in_user["username"],
        turn_limit
    )

This retrieves only records belonging to the logged-in user.

The repository uses a query similar to:

SELECT *
FROM chat_turns
WHERE username = 'analyst01'
ORDER BY turn_id DESC
LIMIT 20;

Step 4: Return the records

return turns

The response contains the previous chat interactions.

In simple words: This endpoint displays the logged-in user's previous Toll Assistant conversations.

15. Endpoint 11 — Audit Chat Turns
Authenticated endpoint GET

@guarded_router.get(
    "/audit/chat-turns",
    response_model=list[ChatTurnResponse]
)
def list_recent_chat_turns(
    turn_limit: int = Query(
        ge=1,
        le=config.CHAT_AUDIT_MAX_ROWS
    )
):

15.1 Theoretical purpose
This endpoint is similar to the previous one, but its purpose is different.

The previous endpoint retrieves the chat history of one user.

This endpoint retrieves recent chat interactions across all users.

Why is this useful?

In an enterprise system, administrators and authorized compliance personnel may need to audit how the AI assistant is being used.

They may want to inspect:

Which questions users asked.

What answers the assistant returned.

Which documents were used.

Whether the assistant refused an answer.

Whether the answer related to a specific dispute.

This is important for compliance, traceability and monitoring.

15.2 Code explanation
Step 1: Receive turn limit

turn_limit: int = Query(
    ge=1,
    le=config.CHAT_AUDIT_MAX_ROWS
)

This works exactly like the previous endpoint.

Step 2: Open database session

with session_factory() as session:

Creates a database session.

Step 3: Fetch records across all users

turns = fetch_chat_turns(
    session,
    true(),
    turn_limit
)

This is the important difference.

Previously:

ChatTurn.username == signed_in_user["username"]

Now:

true()

This comes from SQLAlchemy.

It represents a condition that is always true.

Therefore, the query does not filter by username.

Conceptually:

SELECT *
FROM chat_turns
ORDER BY turn_id DESC
LIMIT 20;

Step 4: Return audit records

return turns

The records are returned using the ChatTurnResponse schema.

Important security observation: Although the endpoint requires authentication, this route does not itself impose a separate role check for auditing. Whether only authorized roles can access it depends on the authorize_request implementation and its path-to-area configuration. You should not assume that every authenticated user is automatically an authorized auditor.

In simple words: This endpoint retrieves recent chatbot interactions across the system for compliance and operational auditing.

16. Helper Function — report_failed_request()
This is not an API endpoint.

It is a helper function used to handle certain failures occurring during API execution.

16.1 Theoretical purpose
Imagine an analyst starts a dispute assessment.

The workflow begins:

Planning agent executes.

Risk assessment agent executes.

Cause identification agent executes.

Tariff advisor encounters an error.

Now the assessment has failed.

Your project should not leave the corresponding agent run marked as running forever.

It needs to record that the execution failed.

This helper function handles that situation.

16.2 Code explanation
def report_failed_request(
    request: Request,
    failure: Exception
):

It receives two arguments:

request: Information about the HTTP request that failed.

failure: The exception that occurred.

Step 1: Retrieve the workflow thread ID

opened_thread_id = getattr(
    request.state,
    "opened_thread_id",
    None
)

Remember this line from the assessment endpoint?

request.state.opened_thread_id = thread_id

Here, we retrieve that same value.

getattr() retrieves an object's attribute safely.

If the attribute doesn't exist, it returns None.

Step 2: Check whether an assessment workflow was started

if opened_thread_id:

Not every API request involves an AI assessment.

For example, a login request doesn't create a LangGraph workflow.

Therefore, the function checks whether a workflow thread ID exists.

Step 3: Retrieve the workflow checkpoint

checkpoint = assessment_graph.get_state(
    {"configurable": {"thread_id": opened_thread_id}}
)

This retrieves the state of the affected workflow.

Step 4: Retrieve the run ID

run_id = checkpoint.values.get("run_id")

The run ID identifies the agent execution record in the database.

Step 5: Check whether a run ID exists

if run_id:

If the workflow has progressed far enough to create a run ID, the system can update its status.

Step 6: Retrieve LLM call records

with session_factory() as session:
    calls = fetch_llm_calls(session, run_id)

This retrieves the recorded language model calls for that run.

Step 7: Mark the agent run as failed

update_agent_run(
    session,
    run_id,
    config.AGENT_RUN_STATUS_FAILED,
    len(calls)
)

This updates the agent run's status and records the number of calls made.

The repository function also sets the finished timestamp for statuses configured as finished statuses.

Step 8: Handle errors during failure reporting

except Exception:
    pass

Why is this present?

Suppose the original request fails, and then the attempt to update the agent run also fails.

We don't want the secondary reporting error to prevent the API from returning its original failure response.

However, this also means that an error during failure reporting is silently ignored.

Step 9: Construct an error message

detail_msg = (
    f"{request.method} {request.url.path} "
    f"could not be completed: {failure}"
)

This creates a descriptive error message.

For example:

POST /assessments could not be completed:
Some service operation failed
Step 10: Return an HTTP response

return JSONResponse(
    status_code=502,
    content={"detail": detail_msg}
)

This returns HTTP 502 Bad Gateway with a JSON error message.

In simple words: This function handles selected backend failures, marks an affected AI execution as failed when possible, and returns a structured error response.

17. Creating the FastAPI Application
Now we have reached the last section of your file.

service_application = FastAPI(
    title=config.API_TITLE
)

What is happening here?
This creates the main FastAPI application instance.

The title comes from your configuration.

Think of FastAPI() as creating the actual backend web application.

Until now, you have defined routers and endpoint functions.

Now you need an application that registers those routers.

Step 2: Register public routes
service_application.include_router(
    public_router
)

This tells FastAPI to include all endpoints belonging to public_router.

These are:

POST /auth/signin
POST /auth/signout
Step 3: Register guarded routes
service_application.include_router(
    guarded_router
)

This registers the authenticated endpoints.

These include:

GET  /queue
GET  /queue/{dispute_reference}

POST /assessments

GET  /disputes
POST /disputes/{assessment_id}/decision
GET  /disputes/{assessment_id}/calls

POST /chat/ask
GET  /chat/turns

GET  /audit/chat-turns
Step 4: Register exception handlers
service_application.add_exception_handler(
    ValueError,
    report_failed_request
)

This tells FastAPI:

Whenever an unhandled ValueError occurs during request processing, use report_failed_request() to handle it.

Similarly:

service_application.add_exception_handler(
    APIError,
    report_failed_request
)

Handles Google GenAI API errors.

And:

service_application.add_exception_handler(
    HTTPError,
    report_failed_request
)

Handles HTTP errors raised by the httpx library.

One important distinction: these handlers apply to the specified exception types, not every possible exception. Also, an HTTPException raised intentionally by your endpoints is handled by FastAPI's standard HTTP exception handling, rather than automatically becoming a 502 through this function.

Final application architecture
Frontend — Streamlit Dashboard

Login, queue, dispute details, manager decisions, chat and audit screens

FastAPI — routes.py

Public Router

Sign in and sign out

Guarded Router

Authentication, disputes, assessments and chat

Exception handling

Failure reporting and workflow status updates

AI services

LangGraph, LLM agents, RAG and ML models

Persistence

SQLAlchemy, database and workflow checkpoints

Business tools

Charge calculations, compensation and predictions

Security

Password hashing, session tokens and authorization

18. Complete summary of all 11 endpoints
This table is particularly useful for revision and interviews.

No.

Endpoint

Method

What it does

1

/auth/signin

POST

Authenticates user and generates session token

2

/auth/signout

POST

Invalidates session token

3

/queue

GET

Retrieves and filters open dispute queue

4

/queue/{dispute_reference}

GET

Retrieves complete details of an individual dispute

5

/assessments

POST

Starts multi-agent AI assessment

6

/disputes

GET

Retrieves assessments based on status

7

/disputes/{assessment_id}/decision

POST

Submits manager decision and resumes workflow

8

/disputes/{assessment_id}/calls

GET

Retrieves LLM call metrics

9

/chat/ask

POST

Answers questions using RAG and dispute records

10

/chat/turns

GET

Retrieves current user's chat history

11

/audit/chat-turns

GET

Retrieves recent chat interactions across users

19. Which files are connected to routes.py?
This is an important part of understanding your complete project.

Your routes.py doesn't implement everything itself. It coordinates several other modules.

Here is the relationship:

File

Responsibility

Used by routes.py for

api/schemas.py

Pydantic models

Request validation and response formatting

config/config.py

Central configuration

Statuses, permissions, limits and messages

access/password_security.py

Password hashing

Login verification

access/permissions.py

Authentication and authorization

Protecting endpoints

persistence/database.py

Database session creation

Database operations

persistence/models.py

SQLAlchemy models

Database table references

persistence/repository.py

Database queries

Fetching and updating records

agentic/graph.py

LangGraph construction

Creating and executing assessment workflow

agentic/nodes.py

Workflow node implementations

AI assessment execution and data loading

agentic/agents.py

LLM agent operations

Indirectly through LangGraph and chatbot

tools/charge_tools.py

Toll charge calculations

Corrected charge, compensation and ranking

tools/prediction_tools.py

ML prediction operations

Restatement, cause and effort facts

tools/dispute_data_tools.py

Dispute data retrieval

Profiles and customer notes

chat/toll_assistant.py

RAG chatbot

Document-based answers

chat/dispute_status_answer.py

Dispute status answers

Database-based chatbot answers

chat/conversation_memory.py

Conversation history

Contextual chatbot questions

20. Important interview questions about routes.py
Let's revise the concepts an interviewer may ask you.

Q1. What is the purpose of routes.py in your project?

routes.py is the API layer of our backend. It defines FastAPI endpoints that allow the frontend to communicate with backend services. It handles authentication, dispute retrieval, AI assessment execution, manager decisions, chatbot interactions and auditing.

Q2. Why did you use FastAPI's APIRouter?

We use APIRouter to organize endpoints into logical groups. We created a public router for authentication and a guarded router for endpoints that require an authenticated session.

Q3. How does authentication work in your project?

When a user signs in, the backend hashes the supplied password using the stored salt and securely compares it with the stored password hash. If authentication succeeds, a random session token is generated and stored in the database. Subsequent requests send this token in an HTTP header, and authorize_request verifies it.

Q4. What is the difference between authentication and authorization?

Authentication verifies who the user is.

Authorization determines what the authenticated user is allowed to do.

Your project implements both through the session token and role-based area permissions.

Q5. Why did you use Pydantic schemas?

Pydantic schemas validate incoming request data and define the expected structure of API responses. They help ensure that endpoints receive valid inputs and return consistent data.

Q6. What is the purpose of the /queue endpoint?

It retrieves the precomputed ranked list of open toll disputes and supports filtering based on discrepancy direction.

Q7. What is the difference between /queue/{dispute_reference} and /assessments?

The queue detail endpoint gathers preliminary dispute information, ML predictions and financial calculations. The assessment endpoint starts the multi-agent LangGraph workflow to generate a comprehensive investigation and recommendation.

Q8. Why did you use LangGraph?

We use LangGraph to orchestrate multiple AI agents in a structured workflow. It allows us to execute investigation steps in sequence, maintain shared state, introduce conditional decision branches and pause execution for manager approval.

Q9. Why do you need a thread ID?

A thread ID identifies an individual LangGraph workflow execution. It allows us to save and retrieve workflow state and resume the correct paused workflow when a manager submits a decision.

Q10. Why is there a manager decision endpoint?

We follow a human-in-the-loop approach. AI agents generate findings and recommendations, but a manager makes the final decision. The endpoint resumes the paused workflow based on that decision.

Q11. What is RAG in your project?

RAG stands for Retrieval-Augmented Generation. Our Toll Assistant retrieves relevant passages from the ChromaDB knowledge collection and provides them as context to an LLM, which generates an answer grounded in the organisation's documents.

Q12. How does your chatbot answer dispute-status questions?

The chatbot first classifies the question. If it identifies a dispute-status question, it extracts the dispute reference and retrieves the actual assessment information from the database. It also applies role-based restrictions to financial information.

Q13. Why do you store chat history?

We store chat history to support conversational context, maintain traceability and enable compliance auditing.

Q14. What is the purpose of report_failed_request()?

It handles selected backend exceptions, attempts to mark an affected agent run as failed and returns a structured HTTP 502 error response.

21. The most important thing to understand about this project
I want you to remember one complete business flow because it connects almost everything in routes.py.

Imagine a toll customer disputes an incorrect charge.

End-to-end toll dispute lifecycle
User signs in

/auth/signin

Backend authenticates the analyst and issues a session token.

Analyst views dispute queue

/queue

Backend returns ranked open disputes with prediction information.

Analyst selects a dispute

/queue/{dispute_reference}

Backend retrieves dispute details, customer notes, charge calculations and ML predictions.

Analyst starts investigation

/assessments

LangGraph executes the multi-agent workflow and creates an assessment.

Manager reviews assessment

/disputes

Manager retrieves assessments awaiting a decision.

Manager makes decision

/disputes/{assessment_id}/decision

Workflow resumes and generates the appropriate settlement documents and outcome.

System tracks AI operations

/disputes/{assessment_id}/calls

Records LLM calls and latency metrics.

Users ask questions

/chat/ask

Toll Assistant retrieves document knowledge or actual dispute status.

System maintains audit history

/chat/turns and /audit/chat-turns

Retrieves personal chat history and cross-user audit records.

This is the overall business purpose of your backend API.

My recommendation for your next learning step: Study agentic/graph.py and agentic/nodes.py next. They are the most important files for understanding what actually happens after the /assessments endpoint is called, including how the AI agents communicate, how workflow state is maintained, and how manager approval resumes execution.





