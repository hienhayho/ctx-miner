import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

#################################################
# CONFIGURATION
#################################################
# Set up logging and environment variables for
# connecting to Neo4j database
#################################################

# Configure logging
logging.basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

falkor_username = os.environ.get("FALKORDB_USERNAME", None)
falkor_password = os.environ.get("FALKORDB_PASSWORD", None)
falkor_host = os.environ.get("FALKORDB_HOST", "localhost")
falkor_port = os.environ.get("FALKORDB_PORT", "6379")
falkor_database = os.environ.get("FALKORDB_DATABASE", "test")

part1 = """User: Chào bạn, bên mình đang có gói cước Internet nào tốc độ cao không?
Assistant: Chào bạn! Hiện tại FPT Telecom đang có gói Super100 với tốc độ 150Mbps, rất phù hợp cho gia đình có nhiều thiết bị dùng cùng lúc. Ngoài ra còn có gói Super200 tốc độ 200Mbps dành cho nhu cầu cao hơn như làm việc từ xa, livestream, hoặc chơi game. Bạn quan tâm đến nhu cầu sử dụng nào để mình tư vấn kỹ hơn?"""

part2 = """User: Nhà mình 5 người, thường xem phim 4K và làm việc online nhiều. Vậy giữa Super100 và Super200 thì gói nào hợp hơn?
Assistant: Với nhu cầu như vậy, mình khuyên bạn chọn Super200 để đảm bảo tốc độ ổn định khi nhiều người dùng đồng thời. Gói này đi kèm với Modem WiFi 6 miễn phí, hỗ trợ đường truyền mạnh hơn trong nhà nhiều tầng. Hiện tại đang có khuyến mãi giảm 15% khi đóng trước 6 tháng. Bạn muốn mình báo giá cụ thể không?"""

part3 = """User: Có ưu đãi nào khi mình đăng ký cả Internet và FPT Play không?
Assistant: Có đấy ạ! Khi bạn đăng ký combo Internet + FPT Play Box, bạn sẽ được:
- Giảm thêm 10% tổng hóa đơn,
- Tặng 12 tháng gói giải trí MAX trên FPT Play (bao gồm phim chiếu rạp, thể thao, HBO, v.v).
Combo phổ biến hiện nay là Super200 + FPT Play Box 2025, chỉ từ 495.000đ/tháng nếu thanh toán trước 6 tháng. Bạn muốn mình lên lịch khảo sát miễn phí không?"""

part4 = """User: Nếu nhà mình đã có TV thông minh thì có cần mua FPT Play Box không?
Assistant: Nếu TV nhà bạn là Smart TV đời mới thì không bắt buộc phải mua thêm FPT Play Box. Bạn có thể cài trực tiếp ứng dụng FPT Play để sử dụng. Tuy nhiên, FPT Play Box mang lại trải nghiệm mượt mà hơn, hỗ trợ giọng nói, điều khiển thông minh, và không bị giới hạn như một số app mặc định trên TV.
Bạn muốn dùng thử bản demo trong 3 ngày không? Mình có thể gửi link kích hoạt qua Zalo hoặc SMS."""

part5 = """User: Được đấy, gửi giúp mình link bản dùng thử nhé.
Assistant: Dạ vâng, bạn vui lòng cung cấp số điện thoại để mình gửi link bản dùng thử FPT Play bản quyền trong 3 ngày nhé. Trong thời gian đó, bạn có thể trải nghiệm toàn bộ nội dung của gói giải trí MAX. Nếu cần hỗ trợ cài đặt, mình cũng có thể hướng dẫn từ xa."""


async def main():
    #################################################
    # INITIALIZATION
    #################################################
    # Connect to Neo4j and set up Graphiti indices
    # This is required before using other Graphiti
    # functionality
    #################################################

    # Initialize Graphiti with Neo4j connection
    # graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
    driver = FalkorDriver(
        host=falkor_host,
        port=falkor_port,
        username=falkor_username,
        password=falkor_password,
        database="test",
    )

    # Pass the driver to Graphiti
    graphiti = Graphiti(graph_driver=driver)

    try:
        # Initialize the graph database with graphiti's indices. This only needs to be done once.
        await graphiti.build_indices_and_constraints()

        #################################################
        # ADDING EPISODES
        #################################################
        # Episodes are the primary units of information
        # in Graphiti. They can be text or structured JSON
        # and are automatically processed to extract entities
        # and relationships.
        #################################################

        # Example: Add Episodes
        # Episodes list containing both text and JSON episodes
        episodes = [
            {
                "content": part1,
                "type": EpisodeType.message,
                "description": "User bắt đầu cuộc hội thoại bằng cách hỏi về các gói Internet tốc độ cao. Assistant giới thiệu hai gói Super100 và Super200, đồng thời gợi mở nhu cầu cụ thể của user.",
            },
            {
                "content": part2,
                "type": EpisodeType.message,
                "description": "User tiếp tục hỏi về nhu cầu sử dụng của mình, giúp Assistant tư vấn gói Super200 phù hợp hơn.",
            },
            {
                "content": part3,
                "type": EpisodeType.message,
                "description": "User hỏi về ưu đãi khi đăng ký combo Internet + FPT Play Box. Assistant giới thiệu ưu đãi giảm 10% và tặng 12 tháng gói giải trí MAX.",
            },
            {
                "content": part4,
                "type": EpisodeType.message,
                "description": "User hỏi về việc có cần mua FPT Play Box nếu đã có Smart TV. Assistant giải thích lợi ích của FPT Play Box và đề xuất dùng thử bản demo.",
            },
            {
                "content": part5,
                "type": EpisodeType.message,
                "description": "User đồng ý dùng thử bản demo. Assistant gửi link kích hoạt qua Zalo hoặc SMS.",
            },
        ]

        # Add episodes to the graph
        for i, episode in enumerate(episodes):
            await graphiti.add_episode(
                name=f"Chatbot {i}",
                episode_body=(
                    episode["content"]
                    if isinstance(episode["content"], str)
                    else json.dumps(episode["content"])
                ),
                source=episode["type"],
                source_description=episode["description"],
                reference_time=datetime.now(timezone.utc),
                group_id="test",
            )
            print(f'Added episode: Chatbot {i} ({episode["type"].value})')

        #################################################
        # BASIC SEARCH
        #################################################
        # The simplest way to retrieve relationships (edges)
        # from Graphiti is using the search method, which
        # performs a hybrid search combining semantic
        # similarity and BM25 text retrieval.
        #################################################

        # Perform a hybrid search combining semantic similarity and BM25 retrieval
        print("\nSearching for: 'Bạn có gói cước Internet nào tốc độ cao không?'")
        results = await graphiti.search(
            "Bạn có gói cước Internet nào tốc độ cao không?",
            group_ids=["test"],
        )

        # Print search results
        print("\nSearch Results:")
        for result in results:
            print(f"UUID: {result.uuid}")
            print(f"Fact: {result.fact}")
            if hasattr(result, "valid_at") and result.valid_at:
                print(f"Valid from: {result.valid_at}")
            if hasattr(result, "invalid_at") and result.invalid_at:
                print(f"Valid until: {result.invalid_at}")
            print("---")

        #################################################
        # CENTER NODE SEARCH
        #################################################
        # For more contextually relevant results, you can
        # use a center node to rerank search results based
        # on their graph distance to a specific node
        #################################################

        # Use the top search result's UUID as the center node for reranking
        if results and len(results) > 0:
            # Get the source node UUID from the top result
            center_node_uuid = results[0].source_node_uuid

            print("\nReranking search results based on graph distance:")
            print(f"Using center node UUID: {center_node_uuid}")

            reranked_results = await graphiti.search(
                "Bạn có gói cước Internet nào tốc độ cao không?",
                center_node_uuid=center_node_uuid,
                group_ids=["test"],
            )

            # Print reranked search results
            print("\nReranked Search Results:")
            for result in reranked_results:
                print(f"UUID: {result.uuid}")
                print(f"Fact: {result.fact}")
                if hasattr(result, "valid_at") and result.valid_at:
                    print(f"Valid from: {result.valid_at}")
                if hasattr(result, "invalid_at") and result.invalid_at:
                    print(f"Valid until: {result.invalid_at}")
                print("---")
        else:
            print("No results found in the initial search to use as center node.")

        #################################################
        # NODE SEARCH USING SEARCH RECIPES
        #################################################
        # Graphiti provides predefined search recipes
        # optimized for different search scenarios.
        # Here we use NODE_HYBRID_SEARCH_RRF for retrieving
        # nodes directly instead of edges.
        #################################################

        # Example: Perform a node search using _search method with standard recipes
        print(
            "\nPerforming node search using _search method with standard recipe NODE_HYBRID_SEARCH_RRF:"
        )

        # Use a predefined search configuration recipe and modify its limit
        node_search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        node_search_config.limit = 5  # Limit to 5 results

        # Execute the node search
        node_search_results = await graphiti._search(
            query="Bạn có gói cước Internet nào tốc độ cao không?",
            config=node_search_config,
            group_ids=["test"],
        )

        # Print node search results
        print("\nNode Search Results:")
        for node in node_search_results.nodes:
            print(f"Node UUID: {node.uuid}")
            print(f"Node Name: {node.name}")
            node_summary = (
                node.summary[:100] + "..." if len(node.summary) > 100 else node.summary
            )
            print(f"Content Summary: {node_summary}")
            print(f'Node Labels: {", ".join(node.labels)}')
            print(f"Created At: {node.created_at}")
            if hasattr(node, "attributes") and node.attributes:
                print("Attributes:")
                for key, value in node.attributes.items():
                    print(f"  {key}: {value}")
            print("---")

    finally:
        #################################################
        # CLEANUP
        #################################################
        # Always close the connection to Neo4j when
        # finished to properly release resources
        #################################################

        # Close the connection
        await graphiti.close()
        print("\nConnection closed")


if __name__ == "__main__":
    asyncio.run(main())
