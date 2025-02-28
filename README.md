# AI Vision Adaptive Face Masking 

  Welcome to **B[U]ILT @ Illinois'** Engineering Open House project! Below you will find a description of the different components that power our project along with some resources to help you get started if you're unfamiliar with any framework or topic mentioned. Also included will be best practices to ensure that our repository runs smoothly.

## Important Starter Info

  - Our EOH Website is currently hosted on AWS at [d1sgrkfj1bwr8d.cloudfront.net](d1sgrkfj1bwr8d.cloudfront.net)
  - If certificates/keys are needed to connect the ml_backend to AWS IoT, please ask @scuruchima1 for certificates and guidance.
  
## ML Backend
  
  Our ML Backend will be comprised of Python and other packages will be best suited for face detection and masking.

## AWS Backend

 Our AWS (Amazon Web Services) Backend will be comprised of Terraform or IaC (Infrastructure as Code) that will allow us to provision backend infrastructure/resources on AWS via code.  

## React Frontend

 Our React Frontend will be the main entry point for users of our project. We will be using the React framework to build our main web app which users will be able to use to send off requests to the ML Backend via the AWS Backend.

## Resources

 1. [**Deep Dive Into Modern Web Development**](https://fullstackopen.com/en/)
 2. [**What is Amazon Web Services?**](https://www.geeksforgeeks.org/introduction-to-amazon-web-services/)
 3. [**About React**](https://react.dev)
  

## Best Practices

  To ensure our repository has less conflicts and to ensure everyone can develop fluidly we will implement best practices on branching, code reviews, descriptive naming/messages, modular reusable code, and commits.

 Please read up on these best practices as well, [**What are Git version control best practices?**](https://about.gitlab.com/topics/version-control/version-control-best-practices/)

### Branching

 Feature branching is a great way for teams to split up work and ensure there are reduced merge conflicts. This also ensures that the scope of pull requests are focused and specific. 

 A branch should be named with a proper name as well to signal to others what the purpose of the banch is, who is working on the branch, and where a feature will be located. 

 For example a branch for a rotating photo carousel feature on an about page by Steven can take on the form:  ***stevenuru/about/rotating-carousel***

### Commits

 Commits to a branch should be done granularly with frequency. Commiting large changes to a codebase can make it difficult for reviewers to gather a sense of what's going on and can make it more difficult to spot errors in one's code merge.

 Branch merges to main should also be reviewed by another committee member to reduce the risk of errors and to maintain a clean codebase.

### Writing Code

 #### Modularity
 
 Code should be written with reusability and modularity in mind. Functions should be used when possible to decrease repetititve code and makes it easier for reviewers to read when done right. Files should also be split up based on the functionality/purpose of the file. 

 #### Comments

 Comments should be used when the code itself cannot communicate to others what is happening. We should strive to use descriptive (although short) comments when defining new functions. This helps ramp up learning whenever someone new is introduced to the codebase
