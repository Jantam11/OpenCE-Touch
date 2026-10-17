# Use the Linux artifact from this fork's CI; supply your own maps at runtime.
FROM archlinux:latest
RUN printf '\n[multilib]\nInclude = /etc/pacman.d/mirrorlist\n' >> /etc/pacman.conf \
 && pacman -Syu --noconfirm --needed python lib32-glibc lib32-gcc-libs lib32-sdl3 \
 && pacman -Scc --noconfirm \
 && useradd --uid 10001 --create-home opence
COPY dist/halo-linux-release/ /opt/opence/halo-linux-release/
COPY server/ /opt/opence/server/
RUN chown -R opence:opence /opt/opence
USER opence
WORKDIR /data
ENTRYPOINT ["python", "/opt/opence/server/run.py", "--executable", "/opt/opence/halo-linux-release/halo", "--data", "/data", "--saves", "/saves"]
