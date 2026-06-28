FROM golang:1.23

WORKDIR /app

# Install uv for python plotting
RUN apt-get update && apt-get install -y python3 python3-pip curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:${PATH}"

COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Pre-install python dependencies
RUN uv venv && uv pip install -r requirements.txt

CMD ["make", "reproduce"]
