# `ast`

**Usage**:

```console
$ ast [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `aws`: AWS related tasks.
* `az`: Azure related tasks.

## `ast aws`

AWS related tasks.

**Usage**:

```console
$ ast aws [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `crane`: Login in to ECR with Crane.
* `podman`: Login in to ECR with Podman.

### `ast aws crane`

Login in to ECR with Crane.

**Usage**:

```console
$ ast aws crane [OPTIONS] REGISTRY
```

**Arguments**:

* `REGISTRY`: The registry to login to.  [required]

**Options**:

* `--profile TEXT`: The AWS profile to use.
* `--help`: Show this message and exit.

### `ast aws podman`

Login in to ECR with Podman.

**Usage**:

```console
$ ast aws podman [OPTIONS] REGISTRY
```

**Arguments**:

* `REGISTRY`: The registry to login to.  [required]

**Options**:

* `--profile TEXT`: The AWS profile to use.
* `--help`: Show this message and exit.

## `ast az`

Azure related tasks.

**Usage**:

```console
$ ast az [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `crane`: Login in to ACR with Crane.
* `podman`: Login in to ACR with Podman.

### `ast az crane`

Login in to ACR with Crane.

**Usage**:

```console
$ ast az crane [OPTIONS] REGISTRY
```

**Arguments**:

* `REGISTRY`: The registry to login to.  [required]

**Options**:

* `--help`: Show this message and exit.

### `ast az podman`

Login in to ACR with Podman.

**Usage**:

```console
$ ast az podman [OPTIONS] REGISTRY
```

**Arguments**:

* `REGISTRY`: The registry to login to.  [required]

**Options**:

* `--help`: Show this message and exit.
