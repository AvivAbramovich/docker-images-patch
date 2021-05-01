ARG base_image

FROM ${base_image}

ARG certs_dir

# RUN sed -i 's/https/http' /etc/apk/repositories
RUN apk update && apk add ca-certificates --allow-untrusted

RUN test -n "${certs_dir}"
ADD ${certs_dir} /usr/local/share/ca-certificates/

RUN update-ca-certificates