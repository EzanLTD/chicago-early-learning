# Early Childhood Education Portal

## About

### Purpose and overview

In order to increase transparency and empower parents, the City of Chicago is partnering with the Smart Chicago Collaborative and the University of Chicago’s Urban Education Lab (UEL) to develop a comprehensive early childhood education web portal. The portal serves as a one-stop-shop for finding early learning programs, assessing program quality, and tracking data about Chicago’s early childhood systems.


The portal is currently deployed to http://chicagoearlylearning.org



### News

http://chicago.cbslocal.com/2012/11/29/city-offers-early-learning-info-online/ (video)

http://www.examiner.com/article/mayor-emanuel-unveils-online-early-learning-portal-to-help-parents-and-families

### Features

* Zoom, pan, and other map manipulation features
* Click on a location and display attribute information
* Compare information about two different locations, side-by-side
* Geographic search (address and radius) and category filters
* Uses the GoogleMaps base map and geocoding API
* Provides Transit directions by leveraging GoogleMaps Transit capabilities
* Embedded Google Analytics to support usage tracking
* All components are open source
* Printable map
* URL for each resource in order to support bookmarking and sharing
* Responsive user interface design that adapts to tablet and web browser (smart phone support is pending)
* Supports SMS search interface
    * User can text a zip code and receive a list of all facilities in it
    * User can get details about a specific facility
* Tested and support on IE8+, Firefox 12+, and Chrome 19+


## Installation

This web application is designed to be deployed using [Ansbile](http://www.ansibleworks.com/) and developed locally with [vagrant](http://www.vagrantup.com).

Requirements:
* vagrant (version 1.3.0+)
* ansible (version 1.2.2)

Development instructions:

* apt-get install vagrant
* pip install ansible
* git clone git://github.com/smartchicago/chicago-early-learning.git
* cd chicago-early-learning
* cp deployment/hosts.example deployment/hosts
* vagrant up

This will create a new Ubuntu 12.04 virtual machine using vagrant. Within the virtual machine Ansible will

* Setup nginx (webserver)
* Setup gunicorn (appserver)
* Start nginx
* Start gunicorn
* Setup postgis
* Create a django local_settings.py file
* Sync the Django models with the database

Open up a browser to http://localhost:8080/ and you should see the application running.

After the VM is set up you will need to create a super user to sign into the admin interface. You can do the following from a terminal in the chicago-early-learning directory:

    vagrant ssh
    source /cel/env/bin/activate
    cd /cel/app/python/ecep
    python manage.py createsuperuser

You will now be able sign into the admin interface at http://localhost:8080/admin

To deploy to another server you will need to modify the `hosts` file `deployment/hosts` and the Ansible playbooks to deploy. This should require little more than setting up credentials for the new host for ssh access from the provisioning computer and modifying those files.

For instance, if you are deploying to a server at `example.com` you would add that to the listing of hosts in `deployment/hosts` and optionally define any new vars to override defaults in a new vars file at `deployment/playbooks/host_vars/example.com` or add the host to an existing group in the hosts file. Then to deploy to that server requires the following ansible command:

    ansible-playbook deployment/playbooks/all.yml --inventory-file=deployment/hosts --limit=example.com --private-key=PRIVATE_KEY_FILE

This will provision the setup to that host assuming you have set up ssh access with an ssh-key. Alternatively, you can use a password with the `--ask-pass` option instead. For more information and options for `ansible-playbook` please check out its [documentation](http://www.ansibleworks.com/docs/).

You also have an option to set up a password restricted website as well (sometimes useful in development). To do so, you can either edit one of the `group_vars` files or pass command line argument to the `ansible-playbook` command. For example:

    ansible-playbook deployment/playbooks/all.yml --inventory-file=deployment/hosts --limit=example.com --private-key=PRIVATE_KEY_FILE -l staging -e "http_auth=Restricted http_user=USERNAME http_password=PASSWORD"

This command will deploy to your staging server defined in the hosts file, setting up a password restricted website in the process.

### To update the FAQs
* Use the Django admin forms to modify/add questions as necessary
* Run './manage.py dumpdata faq.Question > portal/fixtures/question.json'
* Commit the modified json file

## Support

Please log any bugs or errors with the issue tracker on [github](https://github.com/smartchicago/chicago-early-learning/issues).
