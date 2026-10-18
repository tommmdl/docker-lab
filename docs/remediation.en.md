# Updating the images without losing sight of the remaining issues

The first scan found vulnerable copies of msgpack, setuptools and urllib3 inside pip. The API does not use these copies to serve requests. We install the application dependencies during the build, then remove pip and ensurepip from the runtime image. This removes the installation tools themselves; package metadata and the vulnerability scanner remain intact. Adding an application dependency now requires rebuilding the image.

Flask moves from 3.1.2 to 3.1.3. The Debian liblzma5 package moves to 5.8.1-1+deb13u2. Both address findings that had a published fix, including lower and unknown severities.

PostgreSQL stays on 17.11 and Debian Bookworm. The official image still ships gosu built with Go 1.24.6. Our derived image builds the same gosu 1.19 source revision with Go 1.27.2, github.com/moby/sys/user 0.4.1 and golang.org/x/sys 0.44.0. The Dockerfile records the source commit and both base-image digests. It replaces the executable, preserving the upstream entrypoint and database layout.

Compose builds both images. Set API_PORT and API_BASE_URL when running the tests on another port, and COMPOSE_PROJECT_NAME to keep the test volume separate. Never use `down -v` on a database whose data you need.

The before/after reports, remaining vulnerabilities and unchanged blocking policy are tracked in [security-lab](https://github.com/tommmdl/security-lab). Fewer findings do not mean that the images have passed the security gate.
