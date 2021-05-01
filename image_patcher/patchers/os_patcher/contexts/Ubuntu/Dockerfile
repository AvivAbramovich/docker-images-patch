ARG base_image

FROM ${base_image}

ARG certs_dir

RUN apt update && apt install ca-certificates -y

RUN test -n "${certs_dir}"
ADD ${certs_dir} /usr/local/share/ca-certificates/

RUN update-ca-certificates