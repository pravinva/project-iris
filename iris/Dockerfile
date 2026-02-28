ARG HOME="/home/unitycatalog"
ARG ALPINE_VERSION="3.20"

# Build stage, using Amazon Corretto jdk 17 on alpine with arm64 support
FROM amazoncorretto:17-alpine${ALPINE_VERSION}-jdk as base

# Dependencies are installed in $HOME/.cache by sbt
ARG HOME
ENV HOME=$HOME

WORKDIR $HOME

# Copy directories without --parents flag
COPY dev/ ./dev/
COPY build/ ./build/
COPY project/ ./project/
COPY examples/ ./examples/
COPY server/ ./server/
COPY api/ ./api/
COPY clients/ ./clients/
COPY version.sbt build.sbt ./

RUN apk add --no-cache bash && ./build/sbt -info clean package

# Small runtime image
FROM alpine:${ALPINE_VERSION} as runtime

# Specific JAVA_HOME from Amazon Corretto
ARG JAVA_HOME="/usr/lib/jvm/default-jvm"
ARG USER="unitycatalog"
ARG HOME

# Copy Java from base
COPY --from=base $JAVA_HOME $JAVA_HOME

ENV HOME=$HOME \
    JAVA_HOME=$JAVA_HOME \
    PATH="${JAVA_HOME}/bin:${PATH}"

# Copy build artifacts from base stage
COPY --from=base $HOME/examples/ $HOME/examples/
COPY --from=base $HOME/server/ $HOME/server/
COPY --from=base $HOME/api/ $HOME/api/
COPY --from=base $HOME/clients/ $HOME/clients/
COPY --from=base $HOME/target/ $HOME/target/
COPY --from=base $HOME/.cache/ $HOME/.cache/

# Create a service user with read and execute permissions and write permissions of the ./etc directory
RUN apk add --no-cache bash && \
    addgroup -S $USER && \
    adduser -S -G $USER $USER

# Copy remaining directories here for caching optimization
COPY bin/ $HOME/bin/
COPY etc/ $HOME/etc/

# Set permissions
RUN chmod -R 550 $HOME && \
    mkdir -p $HOME/etc/ && \
    chmod -R 770 $HOME/etc/ && \
    chown -R $USER:$USER $HOME

USER $USER

WORKDIR $HOME

CMD ["./bin/start-uc-server"]
