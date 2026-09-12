# Guardian presentation

The sidebar uses a neutral `Guardian workspace` label. Set the public build-time
variable `VITE_GUARDIAN_DISPLAY_NAME` to customize it. This is a presentation label,
not an authenticated identity or a multi-user account feature. Do not put secrets
in Vite variables: they are included in the browser bundle.

For a Vite build, set the variable before `npm run build`. For the Docker build,
pass `--build-arg VITE_GUARDIAN_DISPLAY_NAME="Your workspace"`. Runtime environment
changes do not update an already-built frontend.

Guardian authentication continues to use the backend's `GUARDIAN_USERNAME`,
`GUARDIAN_PASSWORD_HASH`, and `JWT_SECRET` configuration. The username field is
blank until the person signs in. Anonymous youth support requires no guardian login.

The ingestion panel accepts user-authored fictional messages and calls the live
analysis API. Canned training messages are no longer offered in the UI. Demo and
synthetic-data labels remain visible, and aid routing remains explicitly simulated.
Existing records and the underlying single-workspace data model are unchanged.
