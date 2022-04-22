pragma solidity 0.8.6;

import "https://github.com/0xcert/ethereum-erc721/src/contracts/tokens/nf-token-metadata.sol";
import "https://github.com/0xcert/ethereum-erc721/src/contracts/ownership/ownable.sol";

/**
 * @dev This is an example contract implementation of NFToken with metadata extension.
 */

contract MyArtSale is
  NFTokenMetadata,
  Ownable
{
    uint256 tokenid = 0;
  /**
   * @dev Contract constructor. Sets metadata extension `name` and `symbol`.
   */
  constructor(address _owner)
  {
    nftName = "Snap Mint";
    owner= _owner;
    nftSymbol = "Snap Mint";
  }

  /**
   * @dev Mints a new NFT.
   * @param _to The address that will own the minted NFT.
   * @param _uri String representing RFC 3986 URI.
   */
  function mint(
    address _to,
    string calldata _uri
  )
    external
    onlyOwner
  {
    tokenid= tokenid+ 1;
    super._mint(_to, tokenid);
    super._setTokenUri(tokenid, _uri);
  }

}