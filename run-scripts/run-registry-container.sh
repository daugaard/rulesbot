docker run -d --restart unless-stopped --name registry -p 5500:5000 -v ~/apps/volumes/registry:/var/lib/registry registry:2
