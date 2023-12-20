# Encrypting Work Items for additional security

Utilizing Robocorp's Control Room and work items is a powerful solution for getting work done quickly. While Robocorp encrypts all data-at-rest with AES-GCM encryption, you have the option to add an additional encryption layer to work items so they cannot be viewed or use without first decrypting the data.

**This tutorial provides you the Producer Consumer template for storing encypted work items in Control Room**

This template leverages the new Python open-source framework [robo](https://github.com/robocorp/robo), and [libraries](https://github.com/robocorp/robo#libraries) from the same project. In this case, we are focusing on these highlights:

- Producer will encrypt all work items data prior to storing it in Control Room
- Consumer will retrieve all work items from Control Room the decrypt the items for processing
- This example uses Control Room Vault for storing an AES256 encryption key

## What you'll need

To complete this tutorial yourself, you'll need the following:

- A Control Room account

## Steps to reproduce

Once all is installed, do the following (if you follow the names exactly, the code will work without changes):

1. You will first an AES256 encryption key. One can be generated using the **RPA.Crypto** library using the following code:
```python
def minimal_task():
    key = Crypto("AES256")
    my_key = key.generate_key()
    print(my_key)
```

2. Store the Encryption Key in Control Room Vault
  - Name: `aes256`
  - key: `key`


## Code explanation

### 1. Set up your dependencies in the [conda.yaml](conda.yaml) file and declare runnables

Please make sure you are using 28.0.0 which adds in the ability to use higher level encryption packages such as AES256

```yaml
dependencies:
  - python=3.10.12
  - pip=23.2.1
  - robocorp-truststore=0.8.0
  - pip:
    - rpaframework==28.0.0
    - robocorp==1.2.4
```

### 2. Producer

The Producer will convert all data to string as the **RPA.Crypto** library can only encrypt files or strings. The **base64.b64encode** portion of this line converts the encrypted data to a storable string.
```python
base64.b64encode(ENC_KEY.encrypt_string(payload["Name"])).decode("utf-8")
```

## Going cloud ☁️

Now that all runs locally, time to go production-grade. In this section we'll do the following things: upload the project to the Control Room, create a process out of it, set up an email trigger and test it.

### 1. Deploy code to Control Room

While you can upload your project directly from VS Code to the Control Room (Command Palette - Robocorp: Upload Robot to the Control Room), the recommended way is to do it via the git repo. You may fork this repo to your own, or simply just use our example repo directly.

It's easy: Tasks tab under your Workspace, Add Task Package, give it a name, and paste the link to the repo. Done.

### 2. Create a Process

Next up, you'll need to create a Process. Tasks are reusable components that you can use to build sequences of actions. When creating a Process you'll map your chosen Tasks with the Worker runtimes.

Follow the UI again, as the video below shows. Processes, Create a new Process and add your details. Just note the video below is for a different process, so you should name your own process accordingly.

Once that's done, you'll have an opportunity to either set the scheduling, or create an email trigger. We'll choose the latter. In the last step, you can create alerts and callbacks to Slack, Email and as Webhook calls. In this example we set a Slack notification for both successfull and unsuccessful runs.

### 3. Run it manually

Once the Proces is created, time to run it! Hit the Run Process button and choose Run with Input Data, and give a file as an input. Once the run starts, you'll see the producer creating new rows in your local database and then the consumer will use them! 🤞

**Tip:** open the Process run for detailed log on the execution.

